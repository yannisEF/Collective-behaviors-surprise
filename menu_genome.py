import os
import tkinter as tk

from utils import *


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

        self.listbox_genomes = tk.Listbox(self.frame_select_genomes, selectmode='single', **GenomeMenu.listbox_parameters)

        self.frame_select_genomes_buttons = tk.Frame(self.frame_select_genomes)
        self.button_show_genome = tk.Button(self.frame_select_genomes_buttons, text="Show Genome", command=self.show_genome, **GenomeMenu.button_parameters)
        self.button_delete_genome = tk.Button(self.frame_select_genomes_buttons, text="Delete", command=self.delete_genome, **GenomeMenu.button_parameters)
        self.button_save_genome = tk.Button(self.frame_select_genomes_buttons, text="Save Genome", command=self.save_genome, **GenomeMenu.button_parameters)
        self.button_load_genome = tk.Button(self.frame_select_genomes_buttons, text="Load Genome", command=self.load_genome, **GenomeMenu.button_parameters)

        self.button_show_genome.grid(row=1, column=1)
        self.button_delete_genome.grid(row=2, column=1)
        self.button_save_genome.grid(row=1, column=2)
        self.button_load_genome.grid(row=2, column=2)

        self.label_genomes.grid(row=1, column=1)
        self.listbox_genomes.grid(row=2, column=1)
        self.frame_select_genomes_buttons.grid(row=3, column=1)

        self.button_delete_genome["width"] //= 2

        for gen in self.application.genomes:
            self.listbox_genomes.insert('end', "Genome {}".format(gen.id+1))
        self.listbox_genomes.select_set(0)

        # Frame to separate UI elements
        self.frame_separation_1 = tk.Frame(self, **self.frame_separation_parameters)
        
        # Frame to start the evolution process
        self.frame_evolve = tk.Frame(self, **self.frame_general_parameters)

        self.frame_evolve_buttons = tk.Frame(self.frame_evolve)
        self.button_start_evolve = tk.Button(self.frame_evolve_buttons, text="Evolve genomes", command=self.start_evolution, **GenomeMenu.button_parameters)
        self.button_modify_ring_length = tk.Checkbutton(self.frame_evolve_buttons, text="Evolve over Length", command=self.set_modify_ring_length, **GenomeMenu.button_parameters)

        self.button_modify_ring_length.grid(row=1, column=1)
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
    
    def add_genome(self, parameters={}, name=""):
        """
        Adds a genome with given parameters
        """

        new_genome = self.application._load_genome(**parameters)
        self.listbox_genomes.insert("end", "{} {}".format("Genome" if len(name) == 0 else name, new_genome.id+1))

        if len(self.application.genomes) == 1:
            self.application.map.genome_to_show = new_genome.id

    def load_genome(self):
        """
        Loads a genome and adds it to the application
        """
        
        loaded_name, loaded_content = load_file()

        if loaded_name is None:
            return

        self.add_genome(parameters=loaded_content, name=loaded_name)
    
    def set_modify_ring_length(self):
        """
        Evolves the population over different ring lengths if checked
        """

        if (self.application.modify_length == False):
            self.application.modify_length = True
        else:
            self.application.modify_length = False

    def start_evolution(self):
        """
        Starts the evolution process
        """
        if (self.application.modify_length == True):
            for k in range (5, 16, 5): #5, 10, 15 only (temporary)
                self.application.map.ring_length = k
                self.application.play_menu.reset_simulation()
                self.application.genomes = []
                self.application.is_paused = True
                self.application.evolve(genome_to_evolve=self.application.id_to_genome[0])
            self.application.modify_length = False
            self.application.f_name = ""
            self.application.is_paused = False
        else:
            self.application.evolve(genome_to_evolve=self.application.id_to_genome[self.get_selection()-1])
