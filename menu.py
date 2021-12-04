import tkinter as tk

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
        self.master._make_frame()

class GenerationMenu(tk.Frame):
    """
    A side-menu that allows the user the advance through the generations' evolution of the simulation, and to select the current visualization
    """

    def __init__(self, master):
        super().__init__(master)

        self.frame_select = tk.Frame(self)

        self.listbox_generations = tk.Listbox(self.frame_select, selectmode='single')
        self.button_show_generation = tk.Button(self.frame_select, text="Show generation", command=self.show_generation)

        self.listbox_generations.grid(row=1, column=1)
        self.button_show_generation.grid(row=2, column=1)

        self.frame_select.grid(row=1, column=1)

        for gen in self.master.generations:
            self.listbox_generations.insert('end', "Generation {}".format(gen.id))
        self.listbox_generations.select_set(0)

    def show_generation(self):
        """
        Shows on the selected generation on the master's canvas
        """

        index = self.listbox_generations.curselection()
        self.master.map.generation_to_show = int(self.listbox_generations.get(index).split()[-1])