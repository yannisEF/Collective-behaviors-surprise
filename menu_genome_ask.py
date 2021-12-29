import tkinter as tk

from utils import *


class AskMenu(tk.Frame):
    """
    A popup menu that asks the user to select a boxplot's parameters
    """

    frame_ask_parameters = {"borderwidth":1, "relief":"sunken"}
    frame_separation_parameters = {"height":5}
    entry_ask_parameters = {"width":30}

    def __init__(self, master, menu, selection):
        super().__init__(master)

        self.master = master
        self.menu = menu
        self.selection = selection

        frame_separation_0 = tk.Frame(self, **self.frame_separation_parameters)

        frame_ask_title = tk.Frame(self, **self.frame_ask_parameters)
        label_ask_title = tk.Label(frame_ask_title, text="Graph's title")
        self.entry_ask_title = tk.Entry(frame_ask_title, **self.entry_ask_parameters)

        label_ask_title.grid(row=1, column=1)
        self.entry_ask_title.grid(row=2, column=1)

        frame_separation_1 = tk.Frame(self, **self.frame_separation_parameters)

        frame_ask_xLabel = tk.Frame(self, **self.frame_ask_parameters)
        label_ask_xLabel = tk.Label(frame_ask_xLabel, text="X label")
        self.entry_ask_xLabel = tk.Entry(frame_ask_xLabel, **self.entry_ask_parameters)

        label_ask_xLabel.grid(row=1, column=1)
        self.entry_ask_xLabel.grid(row=2, column=1)

        frame_separation_2 = tk.Frame(self, **self.frame_separation_parameters)

        frame_ask_yLabel = tk.Frame(self, **self.frame_ask_parameters)
        label_ask_yLabel = tk.Label(frame_ask_yLabel, text="Y label")
        self.entry_ask_yLabel = tk.Entry(frame_ask_yLabel, **self.entry_ask_parameters)

        label_ask_yLabel.grid(row=1, column=1)
        self.entry_ask_yLabel.grid(row=2, column=1)

        frame_separation_3 = tk.Frame(self, **self.frame_separation_parameters)

        button_show = tk.Button(self, text="Show graph", command=self.show_graph)

        frame_separation_4 = tk.Frame(self, **self.frame_separation_parameters)

        frame_separation_0.grid(row=0, column=1)
        frame_ask_title.grid(row=1, column=1)
        frame_separation_1.grid(row=2, column=1)
        frame_ask_xLabel.grid(row=3, column=1)
        frame_separation_2.grid(row=4, column=1)
        frame_ask_yLabel.grid(row=5, column=1)
        frame_separation_3.grid(row=6, column=1)
        button_show.grid(row=7, column=1)
        frame_separation_4.grid(row=8, column=1)

        self.entry_ask_title.focus_set()

        self.pack()
    
    def show_graph(self):
        """
        Shows the graph and quits the popup
        """

        title = self.entry_ask_title.get()
        xLabel = self.entry_ask_xLabel.get()
        yLabel = self.entry_ask_yLabel.get()

        self.master.destroy()
        self.master.update()

        self.menu.show_boxplots(selection=self.selection, title=title, xLabel=xLabel, yLabel=yLabel)
