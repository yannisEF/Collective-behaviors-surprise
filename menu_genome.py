import os
import tkinter as tk

from utils import *
from menu_genome_ask import AskMenu


class GenomeMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the Genomes' evolution of the simulation, and to select the current visualization
    """

    frame_separation_parameters = {"height":40}
    frame_general_parameters = {"borderwidth":3, "relief":"sunken"}
    listbox_parameters = {"width":40, "height":10}
    button_parameters = {"width":15, "height":1}
    button_parameters_csv = {"width":8, "height":1}

    def __init__(self, master):
        super().__init__(master)

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

        for gen in self.master.genomes:
            self.listbox_genomes.insert('end', "Genome {}".format(gen.id+1))
        self.listbox_genomes.select_set(0)

        # Frame to separate UI elements
        self.frame_separation_1 = tk.Frame(self, **self.frame_separation_parameters)
        
        # Frame to select csv data files
        self.frame_select_csv = tk.Frame(self, **self.frame_general_parameters)
        self.label_csv = tk.Label(self.frame_select_csv, text="CSV selection")

        self.listbox_files = tk.Listbox(self.frame_select_csv, selectmode='multiple', **GenomeMenu.listbox_parameters)

        self.frame_select_csv_buttons = tk.Frame(self.frame_select_csv)
        self.button_load_csv = tk.Button(self.frame_select_csv_buttons, text="Load csv", command=self.load_csv, **GenomeMenu.button_parameters_csv)
        self.button_show_boxplots = tk.Button(self.frame_select_csv_buttons, text="Show boxplots", command=self.ask_boxplots_names)
       
        self.button_load_csv.grid(row=1, column=1)
        self.button_show_boxplots.grid(row=1, column=2)

        self.label_csv.grid(row=1, column=1)
        self.listbox_files.grid(row=2, column=1)
        self.frame_select_csv_buttons.grid(row=3, column=1)

        # Filling the listbox
        for s in os.listdir("Data"):
            self.listbox_files.insert('end', s[:-4])

        # Frame to separate UI elements
        self.frame_separation_csv = tk.Frame(self, **self.frame_separation_parameters)

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
        self.frame_select_csv.grid(row=3, column=1)
        self.frame_separation_csv.grid(row=4, column=1)
        self.frame_evolve.grid(row=5, column=1)
    
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

    def load_csv(self):
        """
        Adds a csv file to the list of csv files
        """
        
        path_to_load = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("csv files", "*.csv")])
        name_to_load = path_to_load.split("/")[-1][:-4]

        if name_to_load in self.listbox_files.get("@1,0", tk.END):
            print("Name already exists. Please select another file or rename it.")
            return

        self.listbox_files.insert("end", name_to_load)
        
    def ask_boxplots_names(self):
        """
        Let the user enter the graph's labels and titles
        """

        AskMenu(tk.Toplevel(self), self, selection=self.listbox_files.curselection())

    @check_selected
    def show_boxplots(self, selection=[], path="Data", title="", xLabel="x", yLabel="y"):
        """
        Shows the boxplot of the currently selected files
        """
        
        list_of_files = ["{}/{}.csv".format(path, self.listbox_files.get(i)) for i in selection]
        read_csv_files(list_of_files, title=title, xLabel=xLabel, yLabel=yLabel)
    
    def set_modify_ring_length(self):
        """
        Evolves the population over different ring lengths if checked
        """

        if (self.master.modify_length == False):
            self.master.modify_length = True
        else:
            self.master.modify_length = False

    def start_evolution(self):
        """
        Starts the evolution process
        """
        if (self.master.modify_length == True):
            for k in range (5, 16, 5): #5, 10, 15 only (temporary)
                self.master.map.ring_length = k
                self.master.play_menu.reset_simulation()
                self.master.genomes = []
                self.master.is_paused = True
                self.master.evolve(genome_to_evolve=self.master.id_to_genome[0])
            self.master.modify_length = False
            self.master.f_name = ""
            self.master.is_paused = False
        else:
            self.master.evolve(genome_to_evolve=self.master.id_to_genome[self.get_selection()-1])
