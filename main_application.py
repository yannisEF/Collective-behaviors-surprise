import cma
import csv
import torch
import numpy as np
import tkinter as tk

from progress.bar import Bar


from genome import Genome
from map_ring import Ring

from menu_play import PlayMenu
from menu_genome import GenomeMenu
from menu_show import ShowMenu

from neural_network import ActionNetwork, PredictionNetwork
from utils import entropy, get_time_stamp


class MainApplication(tk.Frame):
    """
    An application that allows to visualize the simulation, currently only on a ring map.
    """

    frame_side_separation_parameters = {"height":40}
    canvas_parameters = {"width":800, "height":600, "bg":"black"}
    map_parameters = {"width":6, "size":500, "color":"white"}
    agent_parameters = {"size":12, "color":"lightgreen"}

    base_speed = int(1000 / 60)
    default_number_runs = 200
    default_max_generations = 30
    default_history_length = 500
    
    def __init__(self, master, ring_length=25, simulation_speed=1, length_fitness=100, length_score=500, nb_run_fitness=1, nb_genomes=1, nb_agents=20, agent_param={"sensor_range_0":.5, "sensor_range_1":1.0, "speed":.1, "noise":.01}):
        super().__init__(master)
        self.master.resizable(False, False)
        
        self.is_paused = True

        self.nb_run_fitness = nb_run_fitness
        self.length_fitness = length_fitness
        self.length_score = length_score

        self.simulation_speed = simulation_speed

        self.nb_agents = nb_agents
        self.agent_param = agent_param

        self.map = Ring(ring_length=ring_length)

        self.genomes = []
        self.id_to_genome = {}
        for _ in range(nb_genomes):
            self._load_genome()
                
        self.canvas_center = (self.canvas_parameters["width"]//2, self.canvas_parameters["height"]//2)
        self.canvas = tk.Canvas(self, **self.canvas_parameters)
        self.canvas.grid(row=1, column=1)

        bottom_menu = tk.Frame(self)

        self.play_menu = PlayMenu(bottom_menu, self)
        self.master.bind('<space>', self.play_menu.change_pause)

        self.play_menu.grid(row=2, column=1)
        
        side_menu = tk.Frame(self)

        self.genome_menu = GenomeMenu(side_menu, self)
        side_separation = tk.Frame(side_menu, **self.frame_side_separation_parameters)
        self.show_menu = ShowMenu(side_menu, self)

        self.genome_menu.grid(row=1, column=2)
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

    def _load_genome(self, action_network=None, prediction_network=None, new_genome=None, name=None):
        """
        Load a genome with specified action network and prediction network
        """

        new_genome = Genome(action_network=action_network, prediction_network=prediction_network) if new_genome is None else new_genome
        self.genomes.append(new_genome)
        self.id_to_genome[new_genome.id] = new_genome

        for _ in range(self.nb_agents):
            new_agent = new_genome.add_agent(**self.agent_param)
            self.map.add_agent(new_genome.id, new_agent)
        
        if name is not None or name == "":
            new_genome.name = name

        return new_genome

    def _draw_map(self):
        """
        Draws a ring map
        """

        dw = self.canvas_parameters["width"] - self.map_parameters["size"]
        dh = self.canvas_parameters["height"] - self.map_parameters["size"]

        x0, y0 = dw//2, dh//2
        x1, y1 = x0 + self.map_parameters["size"], y0 + self.map_parameters["size"]

        self.canvas.create_oval(x0, y0, x1, y1, fill=self.map_parameters["color"])

        margin = self.map_parameters["width"]
        self.canvas.create_oval(x0 + margin, y0 + margin, x1 - margin, y1 - margin, fill=self.canvas_parameters["bg"])
    
    def _draw_agents(self):
        """
        Draws all of the agents
        """

        for x, y in self.map.position_to_ring(self.map_parameters["size"], self.canvas_center):
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
    
    def _compute_genome_fitness(self, genome_tensor):
        """
        Return the average a genome's fitness over a number of runs (slow)
        """
        
        genome = Genome().from_tensor(torch.Tensor(genome_tensor))
        self._load_genome(new_genome=genome)

        reward = 0
        for _ in range(self.nb_run_fitness):
            self.map.reset(genome_to_reset=genome.id)
            self.map.run(length=self.length_fitness, genome_to_run=genome.id)
            reward += genome.compute_fitness(self.length_fitness)
        
        return reward / self.nb_run_fitness

    def _compute_covered_distance(self, genome):
        """
        Computes the covered distance by the genome, assuming all agents have the same speed
        """

        agents = list(genome.agents.values())
        tau = 0.5 * self.map.ring_length / agents[0].speed

        return sum(abs(agent.position - agent.position_history[-int(tau)]) for agent in agents) / (len(agents) * tau)
    
    def _compute_entropy(self, genome):
        """
        Computes the average entropy of the genome's agents' sensors
        """

        agents = list(genome.agents.values())

        avg_entropy = 0
        for agent in agents:
            ent_0 = sum(map(entropy, [count / self.map.length_sim for count in agent.sensor_0_activation_count]))
            ent_1 = sum(map(entropy, [count / self.map.length_sim for count in agent.sensor_1_activation_count]))
            
            avg_entropy += ent_0 + ent_1
        
        return avg_entropy / (4 * len(agents))
    
    def _compute_largest_cluster_ratio(self, genome):
        """
        Computes the ratio of swarm in the largest cluster
        """

        agents = sorted(list(genome.agents.values()), key=lambda x: x.position)

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
    def evolve(self, max_generations, genome_to_evolve, replace_population=True):
        """
        Evolves the population of genomes
        Returns the best fitness over generations, covered distance, entropy and cluster ratio of the last generation
        """

        # Progress bar
        bar = Bar("Evolving {} {} over {} iterations with a map size of {}".format(genome_to_evolve.name, genome_to_evolve.id+1, max_generations, self.map.ring_length), max=max_generations)
        print("Starting evolution process..", end='\r')

        # CMA-ES
        start_solutions = np.array(genome_to_evolve.to_tensor())
        es = cma.purecma.CMAES(start_solutions, 0.5)

        # Data to register
        gen_fitness = []

        # MAYBE ISSUE HERE OF IGNORING LAST STEP
        i = 0
        while not es.stop() and i < max_generations:
            solutions = es.ask()
            fitness = [self._compute_genome_fitness(gen) for gen in solutions]
            es.tell(solutions, [-fit for fit in fitness]) # minimization so take opposite of fitness

            gen_fitness.append(np.max(fitness))

            bar.next()
            i += 1

        if replace_population is True:
            for gen in self.genomes:
                self.genome_menu.delete_genome(gen.id)
        
        # Progress bar
        print()
        bar = Bar("Evaluating generated solutions", max=len(solutions))
        print("Starting evaluation of generated solutions..", end='\r')

        # Adding the generated genomes to the menu and computing the average of the scores over the population
        covered_distance, entropy, cluster_ratio = 0, 0, 0
        action_network, prediction_network = ActionNetwork(), PredictionNetwork()
        for gen_tensor in solutions:
            action_network.from_tensor(torch.Tensor(gen_tensor[:action_network.total_size]))
            prediction_network.from_tensor(torch.Tensor(gen_tensor[action_network.total_size:]))
            
            genome = self.genome_menu.add_genome(parameters={"action_network":action_network, "prediction_network":prediction_network})

            # Running the genome to compute the scores
            self.map.reset(genome_to_reset=genome.id)
            self.map.run(length=self.length_score, genome_to_run=genome.id)

            covered_distance += self._compute_covered_distance(genome)
            entropy += self._compute_entropy(genome)
            cluster_ratio += self._compute_largest_cluster_ratio(genome)

            bar.next()

        print()
        return gen_fitness, covered_distance / len(solutions), entropy / len(solutions), cluster_ratio / len(solutions)

    def run(self):
        """
        Main loop of the application, runs the simulation at a speed defined by the user
        """

        if self.is_paused is False and len(self.genomes) != 0:
            self.map.run(self.play_menu.scale_speed.get())            
            self._make_frame()

        self.after(int(self.base_speed/self.simulation_speed), self.run)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()