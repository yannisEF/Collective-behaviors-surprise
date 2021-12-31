import os
import tkinter as tk
import matplotlib.pyplot as plt

from utils import *
from menu_ask import AskMenu


class ShowMenu(tk.Frame):
    """
    A side-menu that allows the user to visualize relevant data about the simulation
    """
    
    frame_separation_parameters = {"height":40}
    frame_general_parameters = {"borderwidth":3, "relief":"sunken"}
    listbox_parameters = {"width":40, "height":10}
    button_parameters_csv = {"width":8, "height":1}

    history_parameters = {"color":"blue"}

    def __init__(self, master, application):
        super().__init__(master)
        self.application = application

        # Frame to select csv data files
        self.frame_select_csv = tk.Frame(self, **self.frame_general_parameters)
        self.label_csv = tk.Label(self.frame_select_csv, text="CSV selection")

        self.listbox_files = tk.Listbox(self.frame_select_csv, selectmode='simple', **self.listbox_parameters)
        self.listbox_files.bind('<Return>', self.ask_boxplots_names)

        self.frame_select_csv_buttons = tk.Frame(self.frame_select_csv)
        self.button_load_csv = tk.Button(self.frame_select_csv_buttons, text="Load csv", command=self.load_csv, **self.button_parameters_csv)
        self.button_show_boxplots = tk.Button(self.frame_select_csv_buttons, text="Show boxplots", command=self.ask_boxplots_names)

        self.button_load_csv.grid(row=1, column=1)
        self.button_show_boxplots.grid(row=1, column=2)

        self.label_csv.grid(row=1, column=1)
        self.listbox_files.grid(row=2, column=1)
        self.frame_select_csv_buttons.grid(row=3, column=1)

        # Filling the listbox
        for s in os.listdir("Results"):
            self.listbox_files.insert('end', s[:-4])
        
        frame_separation = tk.Frame(self, **self.frame_separation_parameters)
        
        # Button to show the position history of the agents over a run
        self.frame_other_buttons = tk.Frame(self, **self.frame_general_parameters)
        self.label_other_buttons = tk.Label(self.frame_other_buttons, text="Other")

        self.button_show_history = tk.Button(self.frame_other_buttons, text="Show history", command=self.ask_history_length)

        self.label_other_buttons.grid(row=1, column=1)
        self.button_show_history.grid(row=2, column=1)
        
        self.frame_other_buttons.grid(row=1, column=1)
        frame_separation.grid(row=2, column=1)
        self.frame_select_csv.grid(row=3, column=1)
        
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

    @check_selected
    def show_boxplots(self, path="Results", title="", xLabel="x", yLabel="y"):
        """
        Show the boxplot of the currently selected files
        """

        selected_file = "{}/{}.csv".format(path, self.listbox_files.get(self.selection))
        read_csv_files(selected_file, title=title, xLabel=xLabel, yLabel=yLabel)
    
    def show_history(self, title="Position history", length=500):
        """
        Show the plot of the history over one run of given length
        """

        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Position")

        try:
            length = int(length)
            if length <= 0:
                raise ValueError
        except ValueError:
            length = 500
            print("Invalid number, setting the length to its default value of {}".format(self.application.default_history_length))
            

        self.application.map.reset()

        genome_selected = self.application.id_to_genome[self.selection]

        self.application.is_paused = True
        self.application.map.run(length=length, genome_to_run=genome_selected.id, progress_bar=True)

        # Plotting one line for each agent
        for agent in genome_selected.agents.values():
            # Cutting the history into continuous lines for prettier output
            cut_history = []

            last_pos = -1e9
            for position in agent.position_history:
                if abs(position - last_pos) > 2 * agent.speed:
                    cut_history.append([])
                
                cut_history[-1].append(position)
                last_pos = position

            cum_cut_length = 0
            for history in cut_history:
                plt.plot(list(range(cum_cut_length, cum_cut_length+len(history))), history, **self.history_parameters)
                cum_cut_length += len(history) - 1
                
        self.application.is_paused = False
        plt.show()
   
    def ask_boxplots_names(self, event=None):
        """
        Let the user enter the graph's labels and titles
        """

        self.selection = self.listbox_files.curselection()
        entries = {"title":"Graph's title", "xLabel":"X label", "yLabel":"Y label"}
        AskMenu(tk.Toplevel(self), function=self.show_boxplots, entries=entries)
    
    def ask_history_length(self):
        """
        Let the user enter the simulated run's length
        """

        self.selection = self.application.genome_menu.get_selection()-1
        entries = {"title":"Graph's title", "length":"Simulated run's length"}
        AskMenu(tk.Toplevel(self), function=self.show_history, entries=entries)
