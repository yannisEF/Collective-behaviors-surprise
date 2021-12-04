import tkinter as tk

from agents import Agent
from genome import Genome
from map_ring import Ring

from menu import PlayMenu, GenomeMenu


class MainApplication(tk.Frame):
    """
    An application that allows to visualize the simulation, currently only on a ring map.
    """

    canvas_parameters = {"width":800, "height":600, "bg":"black"}
    map_parameters = {"width":6, "size":500, "color":"white"}
    agent_parameters = {"size":12, "color":"lightgreen"}

    base_speed = int(1000 / 60)
    
    def __init__(self, master, ring_length=25, simulation_speed=1, max_steps=500, nb_genomes=50, nb_agents=20, sensor_range_0=.5, sensor_range_1=1.0, speed=.1, noise=.01):
        super().__init__(master)

        self.is_paused = True

        self.max_steps = max_steps

        self.simulation_speed = simulation_speed

        self.map = Ring(ring_length=ring_length)
        self.genomes = [Genome() for _ in range(nb_genomes)]

        for i, genome in enumerate(self.genomes):
            for _ in range(nb_agents):
                new_agent = self.genomes[i].add_agent(sensor_range_0=sensor_range_0, sensor_range_1=sensor_range_1, speed=speed, noise=noise)
                self.map.add_agent(i, new_agent)
        
        self.Genome_to_show = 0 # id of Genome to show

        self.canvas_center = (self.canvas_parameters["width"]//2, self.canvas_parameters["height"]//2)
        self.canvas = tk.Canvas(self, **self.canvas_parameters)
        self.canvas.grid(row=1, column=1)

        self.play_menu = PlayMenu(self)
        self.play_menu.grid(row=2, column=1)

        self.Genome_menu = GenomeMenu(self)
        self.Genome_menu.grid(row=1, column=2)

        self.pack()

        self._make_frame()
        self.run()
    
    def _draw_map(self):
        """
        Draws a ring map
        """

        dw = self.canvas_parameters["width"] - self.map_parameters["size"]
        dh = self.canvas_parameters["height"] - self.map_parameters["size"]

        x0, y0 = dw//2, dh//2
        x1, y1 = x0 + self.map_parameters["size"], y0 + self.map_parameters["size"]

        self.canvas.create_oval(x0, y0, x1, y1, fill=self.map_parameters["color"])

        margin = self.map_parameters["width"]
        self.canvas.create_oval(x0 + margin, y0 + margin, x1 - margin, y1 - margin, fill=self.canvas_parameters["bg"])
    
    def _draw_agents(self):
        """
        Draws all of the agents
        """

        for x, y in self.map.position_to_ring(self.map_parameters["size"], self.canvas_center):
            x0, y0 = x - self.agent_parameters["size"], y - self.agent_parameters["size"]
            x1, y1 = x + self.agent_parameters["size"], y + self.agent_parameters["size"]
            
            self.canvas.create_oval(x0, y0, x1, y1, fill=self.agent_parameters["color"])
    
    def _make_frame(self):
        """
        Makes a frame of the simulation
        """

        self.canvas.delete('all')
        self._draw_map()
        self._draw_agents()
    
    def run(self):
        """
        Main loop of the application, runs the simulation at a speed defined by the user
        """

        if self.is_paused is False:
            self.map.run(self.play_menu.scale_speed.get())            
            self._make_frame()

        self.after(int(self.base_speed/self.simulation_speed), self.run)

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()