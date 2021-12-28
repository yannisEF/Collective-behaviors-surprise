import tkinter as tk

import cma
import time
import csv
import torch
import numpy as np

from genome import Genome
from map_ring import Ring

from menu import PlayMenu, GenomeMenu
from neural_network import ActionNetwork, PredictionNetwork


class MainApplication(tk.Frame):
    """
    An application that allows to visualize the simulation, currently only on a ring map.
    """

    canvas_parameters = {"width":800, "height":600, "bg":"black"}
    map_parameters = {"width":6, "size":500, "color":"white"}
    agent_parameters = {"size":12, "color":"lightgreen"}

    base_speed = int(1000 / 60)
    
    def __init__(self, master, ring_length=25, simulation_speed=1, length_fitness=100, nb_run_fitness=1, nb_genomes=1, nb_agents=20, agent_param={"sensor_range_0":.5, "sensor_range_1":1.0, "speed":.1, "noise":.01}):
        super().__init__(master)

        self.is_paused = True

        self.nb_run_fitness = nb_run_fitness
        self.length_fitness = length_fitness

        self.simulation_speed = simulation_speed

        self.nb_agents = nb_agents
        self.agent_param = agent_param

        self.map = Ring(ring_length=ring_length)

        self.genomes = []
        self.id_to_genome = {}
        for _ in range(nb_genomes):
            self._load_genome()
            
        self.gen_fitness = []
        self.modify_length = False
        self.fitness_L_fname = ""
        self.covered_dist_L_fname = ""
        
        self.canvas_center = (self.canvas_parameters["width"]//2, self.canvas_parameters["height"]//2)
        self.canvas = tk.Canvas(self, **self.canvas_parameters)
        self.canvas.grid(row=1, column=1)

        self.play_menu = PlayMenu(self)
        self.play_menu.grid(row=2, column=1)

        self.genome_menu = GenomeMenu(self)
        self.genome_menu.grid(row=1, column=2)

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
            self.run()
        return inner

    def _load_genome(self, action_network=None, prediction_network=None, new_genome=None):
        """
        Load a genome with specified action network and prediction network
        """

        new_genome = Genome(action_network=action_network, prediction_network=prediction_network) if new_genome is None else new_genome
        self.genomes.append(new_genome)
        self.id_to_genome[new_genome.id] = new_genome

        for _ in range(self.nb_agents):
            new_agent = new_genome.add_agent(**self.agent_param)
            self.map.add_agent(new_genome.id, new_agent)
        
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

    @_pause_during_execution
    def evolve(self, genome_to_evolve, replace_population=True, max_iteration=30):
        """
        Evolves the population of genomes STILL NEEDS MUTATION ?
        """
        i = 0

        start_solutions = np.array(genome_to_evolve.to_tensor()) # not all genomes?
        es = cma.purecma.CMAES(start_solutions, 0.5)
        while not es.stop() and i < max_iteration:
            solutions = es.ask()
            es.tell(solutions, [-self._compute_genome_fitness(gen) for gen in solutions]) # minimization so take opposite of fitness
            es.disp()

            fitness_min = np.min(solutions)
            data = (i, -fitness_min)
            self.gen_fitness.append(data)

            i += 1
        
        nb = np.random.randint(1, 300)
        
        file_name = 'Data/' + str(nb) +'fitness_over_t_L=' + str(self.map.ring_length) + '.csv';
        with open(file_name,'w+') as out:
            csv_out = csv.writer(out)
            for row in self.gen_fitness:
                csv_out.writerow(row)
        
        if (self.modify_length == True):
            if (i == max_iteration):
                file_name = 'Data/' + str(nb) + 'fitness_over_L.csv';
                if (self.fitness_L_fname == ""):
                    self.fitness_L_fname = file_name
                with open(self.fitness_L_fname,'a+') as out:
                    csv_out = csv.writer(out)
                    last_elem = self.gen_fitness[-1]
                    data = (self.map.ring_length, last_elem[1])
                    csv_out.writerow(data)
                
                file_name2 = 'Data/' + str(nb) + 'covered_distance_over_L.csv';
                if (self.covered_dist_L_fname == ""):
                    self.covered_dist_L_fname = file_name2
                with open(self.covered_dist_L_fname,'a+') as out:
                    csv_out = csv.writer(out)
                    #np.log(self.map.covered_dist/(self.nb_agents*self.map.t)) or np.log(self.map.covered_dist/self.nb_agents)
                    data = (self.map.ring_length, np.log(self.map.covered_dist/(self.nb_agents*self.map.t))) 
                    csv_out.writerow(data)
        
        if (self.modify_length == False):
            if replace_population is True:
                for gen in self.genomes:
                    self.genome_menu.delete_genome(gen.id)
                
        action_network, prediction_network = ActionNetwork(), PredictionNetwork()
        for gen_tensor in solutions:
            action_network.from_tensor(torch.Tensor(gen_tensor[:action_network.total_size]))
            prediction_network.from_tensor(torch.Tensor(gen_tensor[action_network.total_size:]))
            if self.modify_length == False:
                self.genome_menu.add_genome(parameters={"action_network":action_network, "prediction_network":prediction_network})
        
        self.gen_fitness = []
        self.map.covered_dist = 0
        self.map.old_position = None

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