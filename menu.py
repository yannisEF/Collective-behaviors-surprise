import tkinter as tk

from utils import *

class PlayMenu(tk.Frame):
    """
    A user interface that allows to change the speed, pause and restart the application
    """

    scale_parameters = {"from_":1, "to":10}

    def __init__(self, master):
        super().__init__(master)

        self.frame_run = tk.Frame(self)

        self.button_play = tk.Button(self.frame_run, text="Play/Pause", command=self.change_pause)
        self.scale_speed = tk.Scale(self.frame_run, orient=tk.HORIZONTAL, **self.scale_parameters)
        self.button_reset = tk.Button(self.frame_run, text="Reset", command=self.reset_simulation)

        self.button_play.grid(row=1, column=1)
        self.scale_speed.grid(row=2, column=1)
        self.button_reset.grid(row=3, column=1)

        self.frame_run.grid(row=1, column=1)

    def change_pause(self):
        self.master.is_paused = not(self.master.is_paused)

    def reset_simulation(self):
        self.master.canvas.delete('all')
        self.master.map.reset()

        for genome in self.master.genomes:
            genome.fitness = 0

        self.master._make_frame()

class GenomeMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the Genomes' evolution of the simulation, and to select the current visualization
    """

    listbox_parameters = {"width":40, "height":10}
    button_parameters = {"width":15, "height":1}
    frame_separation_parameters = {"width":40, "height":250}

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
        self.frame_separation = tk.Frame(self, **GenomeMenu.frame_separation_parameters)

        # Frame to start the evolution process
        self.frame_evolve = tk.Frame(self)

        self.frame_evolve_buttons = tk.Frame(self.frame_evolve)
        self.button_start_evolve = tk.Button(self.frame_evolve_buttons, text="Evolve genomes", command=self.start_evolution, **GenomeMenu.button_parameters)

        self.button_start_evolve.grid(row=1, column=1)

        self.frame_evolve_buttons.grid(row=1, column=1)

        # Packing frames
        self.frame_select.grid(row=1, column=1)
        self.frame_separation.grid(row=2, column=1)
        self.frame_evolve.grid(row=3, column=1)

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
    
    def delete_genome(self):
        """
        Deletes the selected genome
        """
        
        try:
            genome = self.master.id_to_genome[self.get_selection() - 1]
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
    
    def load_genome(self):
        """
        Loads a genome and adds it to the application
        """
        
        loaded_name, loaded_content = load_file()

        if loaded_name is None:
            return

        new_genome = self.master._load_genome(**loaded_content)
        self.listbox_genomes.insert("end", "{} {}".format(loaded_name, new_genome.id+1))

        if len(self.master.genomes) == 1:
            self.master.map.genome_to_show = new_genome.id
        
    def start_evolution(self):
        """
        Starts the evolution process
        """

        self.master.evolve()
