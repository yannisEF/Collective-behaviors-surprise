import cma
import torch
import numpy as np
import tkinter as tk

from scoop import futures
from progress.bar import Bar

from agents_params import params_ring_agent
from agents_utils import Population
from map import Map2D
from map_ring import MapRing

from menu_play import PlayMenu
from menu_population import PopulationMenu
from menu_show import ShowMenu

from neural_network import ActionNetwork, PredictionNetwork
from utils import entropy, get_time_stamp


class MainApplication(tk.Frame):
    """
    An application that allows to visualize and evolve a simulation.
    """

    frame_side_separation_parameters = {"height":40}
    canvas_parameters = {"width":800, "height":600, "bg":"black"}
    map_parameters = {"width":6, "size":500, "color":"white"}
    agent_parameters = {"size":12, "color":"lightgreen"}

    base_speed = int(1000 / 60)
    default_number_runs = 200
    default_max_generations = 30
    default_history_length = 500
    
    def __init__(
        self,
        master: tk.Tk,
        simulation_speed: float = 1.,
        length_fitness: int = 100,
        length_score: int = 500,
        nb_run_fitness: int = 1,
        nb_populations: int = 1,
        nb_agents: int = 20,
        agent_param: dict = params_ring_agent,
        default_map: Map2D = MapRing,
        map_parameters: dict = {"ring_length":25}
    ) -> None:

        super().__init__(master)
        self.master.resizable(False, False)
        
        self.is_paused = True
        self.simulation_speed = simulation_speed

        self.nb_run_fitness = nb_run_fitness
        self.length_fitness = length_fitness
        self.length_score = length_score

        self.nb_agents = nb_agents
        self.agent_param = agent_param

        self.map = default_map(**map_parameters)
        self.hidden_maps = []

        self.id_to_population = {}
        for _ in range(nb_populations):
            self._load_population()
        self.populations = self.id_to_population.values()
        self.map.reset(input_population=list(self.populations)[0])
                
        self.canvas_center = (self.canvas_parameters["width"]//2, self.canvas_parameters["height"]//2)
        self.canvas = tk.Canvas(self, **self.canvas_parameters)
        self.canvas.grid(row=1, column=1)

        bottom_menu = tk.Frame(self)

        self.play_menu = PlayMenu(bottom_menu, self)
        self.master.bind('<space>', self.play_menu.change_pause)

        self.play_menu.grid(row=2, column=1)
        
        side_menu = tk.Frame(self)

        self.population_menu = PopulationMenu(side_menu, self)
        side_separation = tk.Frame(side_menu, **self.frame_side_separation_parameters)
        self.show_menu = ShowMenu(side_menu, self)

        self.population_menu.grid(row=1, column=2)
        side_separation.grid(row=2, column=2)
        self.show_menu.grid(row=3, column=2)

        bottom_menu.grid(row=2, column=1)
        side_menu.grid(row=1, column=2)

        self.pack()

        self._make_frame()
        self.run()
    
    def _pause_during_execution(function):
        """
        Decorator to pause the simulation during the execution of a function
        """
        
        def inner(self, *args, **kwargs):
            self.is_paused = True
            result = function(self, *args, **kwargs)
            self.is_paused = False
            return result
        return inner

    def _load_population(self, new_population=None, name=None):
        """
        Load a population with specified action network and prediction network
        """

        new_population = Population(
            nb_agents=self.nb_agents,
            action_network=ActionNetwork(**self.map.default_params_action_nn),
            prediction_network=PredictionNetwork(**self.map.default_params_prediction_nn),
            agents_param=self.agent_param,
            name=name
        ) if new_population is None else new_population

        self.id_to_population[new_population.id] = new_population
        
        if name is not None or name != "":
            new_population.name = name

        return new_population

    def _draw_map(self):
        """
        Draws the current map
        """

        self.map.draw_map(self.canvas, self.canvas_parameters, self.map_parameters)
    
    def _draw_agents(self):
        """
        Draws all of the agents
        """

        positions = self.map.get_2D_positions(
            map_size=self.map_parameters["size"],
            canvas_center=self.canvas_center
        )
        
        for x, y in positions:
            x0, y0 = x - self.agent_parameters["size"], y - self.agent_parameters["size"]
            x1, y1 = x + self.agent_parameters["size"], y + self.agent_parameters["size"]
            
            self.canvas.create_oval(x0, y0, x1, y1, fill=self.agent_parameters["color"])
    
    def _make_frame(self):
        """
        Makes a frame of the simulation
        """

        self.canvas.delete('all')
        self._draw_map()
        self._draw_agents()

# ALL SCORES NOT HERE, NOT LINKED TO GRAPH APPLICATION
    def _compute_population_fitness(self, population_tensor):
        """
        Return the average a population's tensor's fitness over a number of runs (slow)
        """
        
        population = Population().from_tensor(torch.Tensor(population_tensor))
        self._load_population(new_population=population)

        reward = 0
        for _ in range(self.nb_run_fitness):
            self.map.reset(population_to_reset=population.id)
            self.map.run(length=self.length_fitness, population_to_run=population.id)
            reward += population.compute_fitness(self.length_fitness)
        
        return reward / self.nb_run_fitness

    def _compute_covered_distance(self, population):
        """
        Computes the covered distance by the population, assuming all agents have the same speed
        """

        agents = list(population.agents.values())
        tau = 0.5 * self.map.ring_length / agents[0].speed

        return sum(abs(agent.position - agent.position_history[-int(tau)]) for agent in agents) / (len(agents) * tau)
    
    def _compute_entropy(self, population):
        """
        Computes the average entropy of the population's agents' sensors
        """

        agents = list(population.agents.values())

        avg_entropy = 0
        for agent in agents:
            ent_0 = sum(map(entropy, [count / self.map.length_sim for count in agent.sensor_0_activation_count]))
            ent_1 = sum(map(entropy, [count / self.map.length_sim for count in agent.sensor_1_activation_count]))
            
            avg_entropy += ent_0 + ent_1
        
        return avg_entropy / (4 * len(agents))
    
    def _compute_largest_cluster_ratio(self, population):
        """
        Computes the ratio of swarm in the largest cluster
        """

        agents = sorted(list(population.agents.values()), key=lambda x: x.position)

        cluster_sizes = [1]
        for i, agent in enumerate(agents):
            if abs(agent.position - agents[(i+1)%len(agents)].position) <= agent.sensor_range_1:
                if i+1 != len(agents):
                    cluster_sizes[-1] += 1
                else:
                    cluster_sizes[-1] += cluster_sizes[0]
                    cluster_sizes[0] = cluster_sizes[-1]
            else:
                cluster_sizes.append(1)
        
        return max(cluster_sizes) / len(agents)

    @_pause_during_execution
    def evolve(self, max_generations, population_to_evolve, replace_population=True):
        """
        Evolves the population with CMA-ES (from a starting point, creates a cloud of points that converge towards optimal)
        Returns the best fitness over generations, covered distance, entropy and cluster ratio of the last generation
        """

        # Progress bar
        bar = Bar("Evolving {} {} over {} iterations with a map size of {}".format(population_to_evolve.name, population_to_evolve.id+1, max_generations, self.map.ring_length), max=max_generations)
        print("Starting evolution process..", end='\r')

        # CMA-ES
        start_solutions = np.array(population_to_evolve.to_tensor())
        es = cma.CMAEvolutionStrategy(start_solutions, 2.5)

        # Data to register
        gen_fitness = []

        # MAYBE ISSUE HERE OF IGNORING LAST STEP
        i = 0
        while not es.stop() and i < max_generations:
            solutions = es.ask()
            fitness = list(futures.map(self._compute_population_fitness, solutions))
            es.tell(solutions, [-fit for fit in fitness]) # minimization so take opposite of fitness

            gen_fitness.append(np.max(fitness))

            bar.next()
            i += 1

        if replace_population is True:
            for gen in self.populations:
                self.population_menu.delete_population(gen.id)
        
        # Progress bar
        print()
        bar = Bar("Evaluating generated solutions", max=len(solutions))
        print("Starting evaluation of generated solutions..", end='\r')

        # Adding the generated populations to the menu and computing the average of the scores over the population
        covered_distance, entropy, cluster_ratio = 0, 0, 0
        action_network, prediction_network = ActionNetwork(), PredictionNetwork()
        for gen_tensor in solutions:
            action_network.from_tensor(torch.Tensor(gen_tensor[:action_network.total_size]))
            prediction_network.from_tensor(torch.Tensor(gen_tensor[action_network.total_size:]))
            
            population = self.population_menu.add_population(parameters={"action_network":action_network, "prediction_network":prediction_network})

            # Running the population to compute the scores
            self.map.reset(population_to_reset=population.id)
            self.map.run(length=self.length_score, population_to_run=population.id)

            covered_distance += self._compute_covered_distance(population)
            entropy += self._compute_entropy(population)
            cluster_ratio += self._compute_largest_cluster_ratio(population)

            bar.next()

        print()
        return gen_fitness, covered_distance / len(solutions), entropy / len(solutions), cluster_ratio / len(solutions)

    def run(self):
        """
        Main loop of the application, runs the simulation at a speed defined by the user
        """

        if self.is_paused is False and len(self.populations) != 0:
            self.map.run(self.play_menu.scale_speed.get())          
            self._make_frame()

        self.after(int(self.base_speed/self.simulation_speed), self.run)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()