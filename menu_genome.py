import os
import csv
import numpy as np
import tkinter as tk

from utils import *
from menu_ask import AskMenu


class GenomeMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the Genomes' evolution of the simulation, and to select the current visualization
    """

    frame_separation_parameters = {"height":40}
    frame_general_parameters = {"borderwidth":3, "relief":"sunken"}
    listbox_parameters = {"width":40, "height":10}
    button_parameters = {"width":15, "height":1}

    def __init__(self, master, application):
        super().__init__(master)
        self.application = application

        # Frame to select genomes
        self.frame_select_genomes = tk.Frame(self, **self.frame_general_parameters)
        self.label_genomes = tk.Label(self.frame_select_genomes, text="Genomes selection")
        self.button_random_genome = tk.Button(self.frame_select_genomes, text="Generate", command=self.add_genome, **self.button_parameters)

        self.listbox_genomes = tk.Listbox(self.frame_select_genomes, selectmode='single', **self.listbox_parameters)

        self.frame_select_genomes_buttons = tk.Frame(self.frame_select_genomes)
        self.button_show_genome = tk.Button(self.frame_select_genomes_buttons, text="Show Genome", command=self.show_genome, **self.button_parameters)
        self.button_delete_genome = tk.Button(self.frame_select_genomes_buttons, text="Delete", command=self.delete_genome, **self.button_parameters)
        self.button_save_genome = tk.Button(self.frame_select_genomes_buttons, text="Save Genome", command=self.save_genome, **self.button_parameters)
        self.button_load_genome = tk.Button(self.frame_select_genomes_buttons, text="Load Genome", command=self.load_genome, **self.button_parameters)

        self.button_show_genome.grid(row=1, column=1)
        self.button_delete_genome.grid(row=2, column=1)
        self.button_save_genome.grid(row=1, column=2)
        self.button_load_genome.grid(row=2, column=2)

        self.label_genomes.grid(row=1, column=1)
        self.button_random_genome.grid(row=1, column=2)
        self.listbox_genomes.grid(row=2, column=1, columnspan=2)
        self.frame_select_genomes_buttons.grid(row=3, column=1, columnspan=2)

        self.button_random_genome["width"] //= 2
        self.button_delete_genome["width"] //= 2

        for gen in self.application.genomes:
            self.listbox_genomes.insert('end', "Genome {}".format(gen.id+1))
        self.listbox_genomes.select_set(0)

        # Frame to separate UI elements
        self.frame_separation_1 = tk.Frame(self, **self.frame_separation_parameters)
        
        # Frame to start the evolution process
        self.frame_evolve = tk.Frame(self, **self.frame_general_parameters)

        self.frame_evolve_buttons = tk.Frame(self.frame_evolve)
        self.button_start_evolve = tk.Button(self.frame_evolve_buttons, text="Evolve genomes", command=self.ask_evolution, **self.button_parameters)

        #   Checkbutton to iterate the evolution process over all lengths
        self.check_modify_ring_length = tk.BooleanVar()
        self.check_modify_ring_length.set(False)

        self.checkbutton_modify_ring_length = tk.Checkbutton(self.frame_evolve_buttons, text="Evolve over Length", var=self.check_modify_ring_length, **self.button_parameters)

        self.checkbutton_modify_ring_length.grid(row=1, column=1)
        self.button_start_evolve.grid(row=2, column=1)

        self.frame_evolve_buttons.grid(row=1, column=1)

        # Packing frames
        self.frame_select_genomes.grid(row=1, column=1)
        self.frame_separation_1.grid(row=2, column=1)
        self.frame_evolve.grid(row=5, column=1)
    
    def get_selection(self):
        """
        Retrieves the current selection
        """

        index = self.listbox_genomes.curselection()
        return int(self.listbox_genomes.get(index).split()[-1])
    
    def show_genome(self):
        """
        Shows on the selected Genome on the application's canvas
        """

        try:
            self.application.map.genome_to_show = self.get_selection() - 1
            self.application._make_frame()
        except tk.TclError:
            pass
    
    def delete_genome(self, id_to_delete=None):
        """
        Deletes the selected or specified genome
        """
        
        try:
            genome = self.application.id_to_genome[id_to_delete if id_to_delete is not None else self.get_selection() - 1]
            self.listbox_genomes.delete(self.listbox_genomes.curselection())

            self.application.genomes.remove(genome)
            del self.application.id_to_genome[genome.id]
            del self.application.map.agents[genome.id]
            del self.application.map.agent_to_pos[genome.id]

            try:
                if self.application.map.genome_to_show == genome.id:
                    self.application.map.genome_to_show = self.application.genomes[0].id
                    self.application._make_frame()
                    
            except IndexError:
                pass
                
            self.listbox_genomes.select_set(0)

            if len(self.application.genomes) == 0:
                self.application.canvas.delete("all")
                self.application._draw_map()
                
        except tk.TclError:
            pass

    def save_genome(self):
        """
        Saves the selected genome in a file
        """
        
        try:
            selected_genome = self.application.id_to_genome[self.get_selection()-1]
            to_save = {"action_network":selected_genome.action_network, "prediction_network":selected_genome.prediction_network}

            save_file(to_save)
        except tk.TclError:
            pass
    
    def add_genome(self, parameters={}, name=None):
        """
        Adds a genome with given parameters
        """

        new_genome = self.application._load_genome(name=name, **parameters)
        self.listbox_genomes.insert("end", "{} {}".format(new_genome.name, new_genome.id+1))

        self.listbox_genomes.selection_clear(0, tk.END)
        self.listbox_genomes.selection_set(tk.END)
        self.listbox_genomes.see("end")

        self.application.map.genome_to_show = new_genome.id
        self.application._make_frame()

        return new_genome

    def load_genome(self):
        """
        Loads a genome and adds it to the application
        """
        
        loaded_name, loaded_content = load_file()

        if loaded_name is None:
            return

        self.add_genome(parameters=loaded_content, name=loaded_name)

    def ask_evolution(self):
        """
        Lets the user choose the evolution process' parameters
        """

        try:
            self.selection = self.get_selection()
            entries = {"output_prefix":"Name prefix of the output (default is timestamp)", "nb_runs":"Number of runs (default 200)", "max_generations":"Maximum number of generations (default 30)"}
            AskMenu(tk.Toplevel(self), function=self.start_evolution, entries=entries)
        except:
            print("Please add a genome to the application and select it.")
            pass
    
    def iterate_evolution(self, nb_runs, max_generations, genome_to_evolve):
        """
        Returns the fitness over the generations, and the scores of the evolution process through the desired number of runs
        """

        conc_gen_fitness = []
        conc_fitness, conc_distance, conc_entropy, conc_ratio = [], [], [], []
        for _ in range(nb_runs):
            print("Run {}/{}".format(_, nb_runs))
            self.application.play_menu.reset_simulation()
            gen_fitness, covered_distance, entropy, cluster_ratio = self.application.evolve(max_generations=max_generations, genome_to_evolve=genome_to_evolve)

            conc_gen_fitness.append(gen_fitness)
            conc_fitness.append(np.max(gen_fitness))
            conc_distance.append(covered_distance)
            conc_entropy.append(entropy)
            conc_ratio.append(cluster_ratio)
        
        return conc_gen_fitness, conc_fitness, conc_distance, conc_entropy, conc_ratio

    def write_evolution(self, path, output_prefix, length, is_iterated, conc_gen_fitness, conc_fitness, conc_distance, conc_entropy, conc_ratio):
        """
        Writes the evolution process' results in separate files with given prefix
        """

        iterated = "all" if is_iterated is True else length

        with open(path.format(output_prefix, "gen_fitness", length), 'a+') as f:
            for gen_fitness in conc_gen_fitness:
                for step, fit in enumerate(gen_fitness):
                    csv.writer(f).writerow((step, fit))

        with open(path.format(output_prefix, "fitness", iterated), 'a+') as f:
            for fitness in conc_fitness:
                csv.writer(f).writerow((length, fitness))

        with open(path.format(output_prefix, "distance", iterated), 'a+') as f:
            for distance in conc_distance:
                csv.writer(f).writerow((length, distance))

        with open(path.format(output_prefix, "entropy", iterated), 'a+') as f:
            for entropy in conc_entropy:
                csv.writer(f).writerow((length, entropy))
        
        with open(path.format(output_prefix, "ratio", iterated), 'a+') as f:
            for ratio in conc_ratio:
                csv.writer(f).writerow((length, ratio))

    def start_evolution(self, output_prefix, nb_runs, max_generations):
        """
        Starts the evolution process
        """

        try:
            nb_runs = int(nb_runs)
            if nb_runs <= 0:
                raise ValueError
        except ValueError:
            nb_runs =  self.application.default_number_runs
            print("Invalid number, setting number of runs to its default value of {}".format(nb_runs))

        try:
            max_generations = int(max_generations)
            if max_generations <= 0:
                raise ValueError
        except ValueError:
            max_generations =  self.application.default_max_generations
            print("Invalid number, setting number of generations to its default value of {}".format(max_generations))
        
        if output_prefix == "":
            output_prefix = get_time_stamp()

        path = "Data/{}_{}_L={}.csv" # prefix, type, mapsize
        
        genome_to_evolve = self.application.id_to_genome[self.selection-1]

        if self.check_modify_ring_length == True:
            for length in self.application.play_menu.list_lengths:
                self.application.map.ring_length = length
                self.write_evolution(path, output_prefix, length, True, *self.iterate_evolution(nb_runs, max_generations, genome_to_evolve))
        else:
            self.write_evolution(path, output_prefix, self.application.map.ring_length, False, *self.iterate_evolution(nb_runs, max_generations, genome_to_evolve))

        
        # if self.modify_length is True:
        #     if i == max_iteration:
        #         file_name = 'Data/' + str(nb) + 'fitness_over_L.csv'
        #         if (self.fitness_L_fname == ""):
        #             self.fitness_L_fname = file_name
        #         with open(self.fitness_L_fname,'a+') as out:
        #             csv_out = csv.writer(out)
        #             last_elem = gen_fitness[-1]
        #             data = (self.map.ring_length, last_elem[1])
        #             csv_out.writerow(data)
                
        #         file_name2 = 'Data/' + str(nb) + 'covered_distance_over_L.csv'
        #         if (self.covered_dist_L_fname == ""):
        #             self.covered_dist_L_fname = file_name2
        #         with open(self.covered_dist_L_fname,'a+') as out:
        #             csv_out = csv.writer(out)
        #             #np.log(self.map.covered_dist/(self.nb_agents*self.map.t)) or np.log(self.map.covered_dist/self.nb_agents)
        #             data = (self.map.ring_length, np.log(self.map.covered_dist/(self.nb_agents*self.map.t))) 
        #             csv_out.writerow(data)
        
        
        # if self.genome_menu.check_modify_ring_length != True:
        #     # Saving the results in a csv file
        #     filename = 'Data/' + get_time_stamp() + 'best_fitness_L=' + str(self.map.ring_length) + '.csv'
        #     with open(filename,'w+') as out:
        #         csv_out = csv.writer(out)
        #         for i, row in enumerate(gen_fitness):
        #             csv_out.writerow((i,row))