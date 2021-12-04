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
    A menu that allows the user the advance through the generations of the simulation
    """

    def __init__(self, master):
        super().__init__(master)

class ParametersMenu(tk.Frame):
    """
    A side menu that allows to define the simulation's parameters
    """

    def __init__(self, master):
        super().__init__(master)

        # Apply changes button

        # Agent parameters

        # Map parameters

        # Generations parameters