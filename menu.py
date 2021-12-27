from os import name
import os
import tkinter as tk

from map_ring import Ring
from utils import *

class PlayMenu(tk.Frame):
    """
    A user interface that allows to change the speed, pause and restart the application
    """

    scale_parameters = {"from_":1, "to":10}
    frame_separation_parameters = {"width":80, "height":0}
    
    def __init__(self, master):
        super().__init__(master)

        self.frame_run = tk.Frame(self)
        self.frame_separation = tk.Frame(self, **self.frame_separation_parameters)
        self.frame_run2 = tk.Frame(self)
        
        self.button_play = tk.Button(self.frame_run, text="Play/Pause", command=self.change_pause)
        self.scale_speed = tk.Scale(self.frame_run, orient=tk.HORIZONTAL, **self.scale_parameters)
        self.button_reset = tk.Button(self.frame_run, text="Reset", command=self.reset_simulation)

        self.scale_ring_length = tk.Scale(self.frame_run2, orient=tk.VERTICAL, from_=5, to=30, tickinterval=5, length=100, label="Ring Length")
        self.button_modify_length = tk.Button(self.frame_run2, text="Modify", command=self.modify_ring_length)
        
        self.button_play.grid(row=1, column=1)
        self.scale_speed.grid(row=2, column=1)
        self.button_reset.grid(row=3, column=1)
        
        self.scale_ring_length.grid(row=1, rowspan=3, column=1)
        self.button_modify_length.grid(row=1, column=2)

        self.frame_run.grid(row=1, column=1)
        self.frame_separation.grid(row=1, column=2)
        self.frame_run2.grid(row=1, column=3)

    def change_pause(self):
        self.master.is_paused = not(self.master.is_paused)

    def reset_simulation(self):
        self.master.canvas.delete('all')
        self.master.map.reset()

        for genome in self.master.genomes:
            genome.fitness = 0
            
        self.master._make_frame()
    
    def modify_ring_length(self):
        self.master.map.ring_length = self.scale_ring_length.get()
        self.reset_simulation()
    
    
class GenomeMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the Genomes' evolution of the simulation, and to select the current visualization
    """

    listbox_parameters = {"width":40, "height":10}
    button_parameters = {"width":15, "height":1}
    button_parameters2 = {"width":25, "height":1}
    frame_separation_parameters = {"width":40, "height":80}

    def __init__(self, master):
        super().__init__(master)

        # Frame to select genomes
        self.frame_select = tk.Frame(self)

        self.listbox_genomes = tk.Listbox(self.frame_select, selectmode='single', **GenomeMenu.listbox_parameters)

        self.frame_select_buttons = tk.Frame(self.frame_select)
        self.button_show_genome = tk.Button(self.frame_select_buttons, text="Show Genome", command=self.show_genome, **GenomeMenu.button_parameters)
        self.button_delete_genome = tk.Button(self.frame_select_buttons, text="Delete", command=self.delete_genome, **GenomeMenu.button_parameters)
        self.button_save_genome = tk.Button(self.frame_select_buttons, text="Save Genome", command=self.save_genome, **GenomeMenu.button_parameters)
        self.button_load_genome = tk.Button(self.frame_select_buttons, text="Load Genome", command=self.load_genome, **GenomeMenu.button_parameters)

        self.button_show_genome.grid(row=1, column=1)
        self.button_delete_genome.grid(row=2, column=1)
        self.button_save_genome.grid(row=1, column=2)
        self.button_load_genome.grid(row=2, column=2)

        self.listbox_genomes.grid(row=1, column=1)
        self.frame_select_buttons.grid(row=2, column=1)

        self.button_delete_genome["width"] //= 2

        for gen in self.master.genomes:
            self.listbox_genomes.insert('end', "Genome {}".format(gen.id+1))
        self.listbox_genomes.select_set(0)

        # Frame to separate UI elements
        self.frame_separation2 = tk.Frame(self, **GenomeMenu.frame_separation_parameters)
        
        # Frame to select csv data files
        self.frame_select2 = tk.Frame(self)
         
        self.listbox_files = tk.Listbox(self.frame_select2, selectmode='multiple', **GenomeMenu.listbox_parameters)

        self.frame_select_buttons2 = tk.Frame(self.frame_select2)
        self.button_show1 = tk.Button(self.frame_select_buttons2, text="Show best Fitness over gens", command=self.show_boxplots1, **GenomeMenu.button_parameters2)
        self.button_show2 = tk.Button(self.frame_select_buttons2, text="Show best Fitness over L", command=self.show_boxplots2, **GenomeMenu.button_parameters2)
        self.button_show3 = tk.Button(self.frame_select_buttons2, text="Show covered Distance over L", command=self.show_boxplots3, **GenomeMenu.button_parameters2)
       
        self.button_show1.grid(row=1, column=1)
        self.button_show2.grid(row=2, column=1)
        self.button_show3.grid(row=3, column=1)

        self.listbox_files.grid(row=1, column=1)
        self.frame_select_buttons2.grid(row=2, column=1)
        
        # Frame to separate UI elements
        self.frame_separation = tk.Frame(self, **GenomeMenu.frame_separation_parameters)

        # Frame to start the evolution process
        self.frame_evolve = tk.Frame(self)

        self.frame_evolve_buttons = tk.Frame(self.frame_evolve)
        self.button_start_evolve = tk.Button(self.frame_evolve_buttons, text="Evolve genomes", command=self.start_evolution, **GenomeMenu.button_parameters)
        self.button_modify_ring_length = tk.Checkbutton(self.frame_evolve_buttons, text="Evolve over Length", command=self.set_modify_ring_length, **GenomeMenu.button_parameters)

        self.button_modify_ring_length.grid(row=1, column=1)
        self.button_start_evolve.grid(row=2, column=1)

        self.frame_evolve_buttons.grid(row=1, column=1)

        # Packing frames
        self.frame_select.grid(row=1, column=1)
        self.frame_separation2.grid(row=2, column=1)
        self.frame_select2.grid(row=3, column=1)
        self.frame_separation.grid(row=4, column=1)
        self.frame_evolve.grid(row=5, column=1)
        
        self.fill_listbox_files()
    
    def fill_listbox_files(self):
        for s in os.listdir("Data"):
            self.listbox_files.insert('end', s)
    
    def show_boxplots1(self):
        
        index = self.listbox_files.curselection()
        list_of_files = []
        for i in index:
            list_of_files.append("Data/"+self.listbox_files.get(i))
        read_csv_files(list_of_files, title="Best Fitness over generations t", xLabel="t", yLabel="F")
            
    def show_boxplots2(self):
        
        index = self.listbox_files.curselection()
        list_of_files = []
        for i in index:
            list_of_files.append("Data/"+self.listbox_files.get(i), title="Best Fitness of last generation over ring length L", xLabel="L", yLabel="F")
        read_csv_files(list_of_files)
        
    def show_boxplots3(self):
        return
    
    def set_modify_ring_length(self):
        if (self.master.modify_length == False):
            self.master.modify_length = True
        else:
            self.master.modify_length = False
    
    def get_selection(self):
        """
        Retrieves the current selection
        """

        index = self.listbox_genomes.curselection()
        return int(self.listbox_genomes.get(index).split()[-1])
    
    def show_genome(self):
        """
        Shows on the selected Genome on the master's canvas
        """

        try:
            self.master.map.genome_to_show = self.get_selection() - 1
            self.master._make_frame()
        except tk.TclError:
            pass
    
    def delete_genome(self, id_to_delete=None):
        """
        Deletes the selected or specified genome
        """
        
        try:
            genome = self.master.id_to_genome[id_to_delete if id_to_delete is not None else self.get_selection() - 1]
            self.listbox_genomes.delete(self.listbox_genomes.curselection())

            self.master.genomes.remove(genome)
            del self.master.id_to_genome[genome.id]
            del self.master.map.agents[genome.id]
            del self.master.map.agent_to_pos[genome.id]

            try:
                if self.master.map.genome_to_show == genome.id:
                    self.master.map.genome_to_show = self.master.genomes[0].id
                    self.master._make_frame()
                    
            except IndexError:
                pass
                
            self.listbox_genomes.select_set(0)

            if len(self.master.genomes) == 0:
                self.master.canvas.delete("all")
                self.master._draw_map()
                
        except tk.TclError:
            pass

    def save_genome(self):
        """
        Saves the selected genome in a file
        """
        
        try:
            selected_genome = self.master.id_to_genome[self.get_selection()-1]
            to_save = {"action_network":selected_genome.action_network, "prediction_network":selected_genome.prediction_network}

            save_file(to_save)
        except tk.TclError:
            pass
    
    def add_genome(self, parameters={}, name=""):
        """
        Adds a genome with given parameters
        """

        new_genome = self.master._load_genome(**parameters)
        self.listbox_genomes.insert("end", "{} {}".format("Genome" if len(name) == 0 else name, new_genome.id+1))

        if len(self.master.genomes) == 1:
            self.master.map.genome_to_show = new_genome.id

    def load_genome(self):
        """
        Loads a genome and adds it to the application
        """
        
        loaded_name, loaded_content = load_file()

        if loaded_name is None:
            return

        self.add_genome(parameters=loaded_content, name=loaded_name)
            
    def start_evolution(self):
        """
        Starts the evolution process
        """
        if (self.master.modify_length == True):
            for k in range (5, 16, 5): #5, 10, 15 only (temporary)
                self.master.map.ring_length = k
                self.master.play_menu.reset_simulation();
                self.master.genomes = []
                self.master.is_paused = True
                self.master.evolve(genome_to_evolve=self.master.id_to_genome[0])
            self.master.modify_length = False
            self.master.f_name = ""
            self.master.is_paused = False
        else:
            self.master.evolve(genome_to_evolve=self.master.id_to_genome[self.get_selection()-1])
