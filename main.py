from agents import Agent
from map_ring import Ring

ring = Ring(ring_length=10, resolution=.25)

sensor_range_0 = 0.5
sensor_range_1 = 1.0
speed = .25
noise = .001

for _ in range(5):
    ring.add_agent(Agent(sensor_range_0, sensor_range_1, speed, noise))

ring.show()
while True:
    ring._step()
    ring.show()