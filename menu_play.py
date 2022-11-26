import tkinter as tk

from utils import *


class PlayMenu(tk.Frame):
    """
    A user interface that allows to change the speed, pause and restart the application
    """

    scale_speed_parameters = {"from_":1, "to":10}
    scale_length_parameters = {"from_":5, "to":50, "resolution":5}
    frame_separation_parameters = {"width":80, "height":0}
    frame_general_parameters = {"borderwidth":3, "relief":"sunken"}

    scale_length_default = 25
    
    def __init__(self, master, application):
        super().__init__(master)
        self.application = application

        self.frame_run = tk.Frame(self, **self.frame_general_parameters)
        self.frame_separation = tk.Frame(self, **self.frame_separation_parameters)
        self.frame_length = tk.Frame(self, **self.frame_general_parameters)
        
        self.button_play = tk.Button(self.frame_run, text="Play/Pause", command=self.change_pause)
        self.scale_speed = tk.Scale(self.frame_run, orient=tk.HORIZONTAL, label="Simulation speed", **self.scale_speed_parameters)
        self.button_reset = tk.Button(self.frame_run, text="Reset", command=self.reset_simulation)

        self.list_lengths = list(range(self.scale_length_parameters["from_"], self.scale_length_parameters["to"]+1, self.scale_length_parameters["resolution"]))
        self.scale_length = tk.Scale(self.frame_length, orient=tk.HORIZONTAL, label="Ring length", **self.scale_length_parameters)
        self.button_modify_length = tk.Button(self.frame_length, text="Modify", command=self.modify_ring_length)
        
        self.button_play.grid(row=1, column=1)
        self.scale_speed.grid(row=2, column=1)
        self.button_reset.grid(row=3, column=1)
        
        self.button_modify_length.grid(row=1, column=1)
        self.scale_length.grid(row=2, column=1)   

        self.frame_run.grid(row=1, column=1)
        self.frame_separation.grid(row=1, column=2)
        self.frame_length.grid(row=1, column=3)

        self.scale_length.set(25)

    def change_pause(self, event=None):
        """
        Pauses/Runs the selected population
        """

        self.application.is_paused = not(self.application.is_paused)

    def reset_simulation(self):
        """
        Resets the simulation
        """

        self.application.canvas.delete('all')
        self.application.map.reset()

        for population in self.application.populations:
            population.fitness = 0
            
        self.application._make_frame()
    
    def modify_ring_length(self):
        """
        Changes the map's length
        """

        self.application.map.ring_length = self.scale_length.get()
        self.reset_simulation()
