import tkinter as tk

from utils import *


class AskMenu(tk.Frame):
    """
    A pop-up menu that asks the user to enter a function's parameters
    """

    frame_ask_parameters = {"borderwidth":1, "relief":"sunken"}
    frame_separation_parameters = {"height":5}
    entry_ask_parameters = {"width":30}

    def __init__(self, master, function, entries:dict):
        """
        function is the function to be called when the user clicks on the confirm button
        entries is a dictionnary containing: name of function's input variable:text label
        """
        super().__init__(master)

        self.master = master

        self.function = function
        self.entries = entries

        self.list_entry_ask = []
        for i, k in enumerate(self.entries.keys()):
            frame_separation = tk.Frame(self, **self.frame_separation_parameters)
            frame_ask = tk.Frame(self, **self.frame_ask_parameters)
            label_ask = tk.Label(frame_ask, text=self.entries[k])
            self.list_entry_ask.append(tk.Entry(frame_ask, **self.entry_ask_parameters))

            self.list_entry_ask[-1].bind('<Return>', self.confirm)

            label_ask.grid(row=1, column=1)
            self.list_entry_ask[-1].grid(row=2, column=1)

            frame_separation.grid(row=2*i, column=1)
            frame_ask.grid(row=2*i+1, column=1)

        frame_separation_2 = tk.Frame(self, **self.frame_separation_parameters)

        button_confirm = tk.Button(self, text="Confirm", command=self.confirm)

        frame_separation_3 = tk.Frame(self, **self.frame_separation_parameters)

        offset = 2*(len(self.entries)+1)
        frame_separation_2.grid(row=offset, column=1)
        button_confirm.grid(row=offset+1, column=1)
        frame_separation_3.grid(row=offset+2, column=1)

        self.list_entry_ask[0].focus_set()

        self.pack()
    
    def confirm(self, event=None):
        """
        Shows the graph and quits the popup
        """

        user_input = [entry.get() for entry in self.list_entry_ask]

        keys = list(self.entries)
        kwargs = {keys[i]:user_input[i] for i in range(len(self.entries))}

        self.master.destroy()
        self.master.update()

        self.function(**kwargs)
