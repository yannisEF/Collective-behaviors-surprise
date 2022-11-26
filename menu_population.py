import os
import csv
import numpy as np
import tkinter as tk

from utils import *
from menu_ask import AskMenu


class PopulationMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the Populations' evolution of the simulation, and to select the current visualization
    """

    frame_separation_parameters = {"height":40}
    frame_general_parameters = {"borderwidth":3, "relief":"sunken"}
    listbox_parameters = {"width":40, "height":10}
    button_parameters = {"width":15, "height":1}

    def __init__(self, master, application):
        super().__init__(master)
        self.application = application

        # Frame to select populations
        self.frame_select_populations = tk.Frame(self, **self.frame_general_parameters)
        self.label_populations = tk.Label(self.frame_select_populations, text="Populations selection")
        self.button_random_population = tk.Button(self.frame_select_populations, text="Generate", command=self.add_population, **self.button_parameters)

        self.listbox_populations = tk.Listbox(self.frame_select_populations, selectmode='single', **self.listbox_parameters)
        self.listbox_populations.bind('<Return>', self.show_population)

        self.frame_select_populations_buttons = tk.Frame(self.frame_select_populations)
        self.button_show_population = tk.Button(self.frame_select_populations_buttons, text="Show Population", command=self.show_population, **self.button_parameters)
        self.button_delete_population = tk.Button(self.frame_select_populations_buttons, text="Delete", command=self.delete_population, **self.button_parameters)
        self.button_save_population = tk.Button(self.frame_select_populations_buttons, text="Save Population", command=self.save_population, **self.button_parameters)
        self.button_load_population = tk.Button(self.frame_select_populations_buttons, text="Load Population", command=self.load_population, **self.button_parameters)

        self.button_show_population.grid(row=1, column=1)
        self.button_delete_population.grid(row=2, column=1)
        self.button_save_population.grid(row=1, column=2)
        self.button_load_population.grid(row=2, column=2)

        self.label_populations.grid(row=1, column=1)
        self.button_random_population.grid(row=1, column=2)
        self.listbox_populations.grid(row=2, column=1, columnspan=2)
        self.frame_select_populations_buttons.grid(row=3, column=1, columnspan=2)

        self.button_random_population["width"] //= 2
        self.button_delete_population["width"] //= 2

        for gen in self.application.populations:
            self.listbox_populations.insert('end', "Population {}".format(gen.id+1))
        self.listbox_populations.select_set(0)

        # Frame to separate UI elements
        self.frame_separation_1 = tk.Frame(self, **self.frame_separation_parameters)
        
        # Frame to start the evolution process
        self.frame_evolve = tk.Frame(self, **self.frame_general_parameters)

        self.frame_evolve_buttons = tk.Frame(self.frame_evolve)
        self.button_start_evolve = tk.Button(self.frame_evolve_buttons, text="Evolve populations", command=self.ask_evolution, **self.button_parameters)

        #   Checkbutton to iterate the evolution process over all lengths
        self.check_modify_ring_length = tk.BooleanVar()
        self.check_modify_ring_length.set(False)

        self.checkbutton_modify_ring_length = tk.Checkbutton(self.frame_evolve_buttons, text="Evolve over Length", var=self.check_modify_ring_length, **self.button_parameters)

        self.checkbutton_modify_ring_length.grid(row=1, column=1)
        self.button_start_evolve.grid(row=2, column=1)

        self.frame_evolve_buttons.grid(row=1, column=1)

        # Packing frames
        self.frame_select_populations.grid(row=1, column=1)
        self.frame_separation_1.grid(row=2, column=1)
        self.frame_evolve.grid(row=5, column=1)
    
    def get_selection(self):
        """
        Retrieves the current selection
        """

        index = self.listbox_populations.curselection()
        return int(self.listbox_populations.get(index).split()[-1])
    
    def show_population(self, event=None):
        """
        Shows on the selected Population on the application's canvas
        """

        try:
            self.application.map.population_to_show = self.get_selection() - 1
            self.application._make_frame()
        except tk.TclError:
            pass
    
    def delete_population(self, id_to_delete=None):
        """
        Deletes the selected or specified population
        """
        
        try:
            population = self.application.id_to_population[id_to_delete if id_to_delete is not None else self.get_selection() - 1]
            self.listbox_populations.delete(self.listbox_populations.curselection())

            self.application.populations.remove(population)
            del self.application.id_to_population[population.id]
            del self.application.map.agents[population.id]
            del self.application.map.agent_to_pos[population.id]

            try:
                if self.application.map.population_to_show == population.id:
                    self.application.map.population_to_show = self.application.populations[0].id
                    self.application._make_frame()
                    
            except IndexError:
                pass
                
            self.listbox_populations.select_set(0)

            if len(self.application.populations) == 0:
                self.application.canvas.delete("all")
                self.application._draw_map()
                
        except tk.TclError:
            pass

    def save_population(self):
        """
        Saves the selected population in a file
        """
        
        try:
            selected_population = self.application.id_to_population[self.get_selection()-1]
            to_save = {"action_network":selected_population.action_network, "prediction_network":selected_population.prediction_network}

            save_file(to_save)
        except tk.TclError:
            pass
    
    def add_population(self, parameters={}, name=None):
        """
        Adds a population with given parameters
        """

        new_population = self.application._load_population(name=name, **parameters)
        self.listbox_populations.insert("end", "{} {}".format(new_population.name, new_population.id+1))

        self.listbox_populations.selection_clear(0, tk.END)
        self.listbox_populations.selection_set(tk.END)
        self.listbox_populations.see("end")

        self.application.map.population_to_show = new_population.id
        self.application._make_frame()

        return new_population

    def load_population(self):
        """
        Loads a population and adds it to the application
        """
        
        loaded_name, loaded_content = load_file()

        if loaded_name is None:
            return

        self.add_population(parameters=loaded_content, name=loaded_name)

    def ask_evolution(self):
        """
        Lets the user choose the evolution process' parameters
        """

        try:
            self.selection = self.get_selection()
            entries = {"output_prefix":"Name prefix of the output (default is timestamp)", "nb_runs":"Number of runs (default 200)", "max_generations":"Maximum number of generations (default 30)"}
            AskMenu(tk.Toplevel(self), function=self.start_evolution, entries=entries)
        except:
            print("Please add a population to the application and select it.")
            pass
    
    def iterate_evolution(self, nb_runs, max_generations, population_to_evolve):
        """
        Returns the fitness over the generations, and the scores of the evolution process through the desired number of runs
        """

        conc_gen_fitness = []
        conc_fitness, conc_distance, conc_entropy, conc_ratio = [], [], [], []
        for _ in range(nb_runs):
            print("Run {}/{}".format(_+1, nb_runs))
            self.application.play_menu.reset_simulation()
            gen_fitness, covered_distance, entropy, cluster_ratio = self.application.evolve(max_generations=max_generations, population_to_evolve=population_to_evolve)

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

        path = "Results/{}_{}_L={}.csv" # prefix, type, mapsize
        
        population_to_evolve = self.application.id_to_population[self.selection-1]

        if self.check_modify_ring_length.get() == True:
            for length in self.application.play_menu.list_lengths:
                self.application.map.ring_length = length
                self.write_evolution(path, output_prefix, length, True, *self.iterate_evolution(nb_runs, max_generations, population_to_evolve))
        else:
            self.write_evolution(path, output_prefix, self.application.map.ring_length, False, *self.iterate_evolution(nb_runs, max_generations, population_to_evolve))
