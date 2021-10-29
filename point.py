import numpy as np
import pygame
from numba import int32, float32, boolean
from numba.experimental import jitclass

spec = [
    ('position', float32[:]),
    ('prev_position', float32[:]),
    ('velocity', float32[:]),
    ('prev_velocity', float32[:]),
    ('applied_force', float32[:]),
    ('mass', float32),
    ('static', boolean),
    ('color', int32[:])
]


# @jitclass(spec)
class Point:
    def __init__(self, position, static=False, mass=1):
        self.position = np.array(position, dtype=np.float64)
        self.prev_position = self.position.copy()
        self.velocity = np.array([0, 0], dtype=np.float64)
        self.prev_velocity = np.array([0, 0], dtype=np.float64)
        self.applied_force = np.array([0, 0], dtype=np.float64)
        self.mass = mass
        self.color = np.array([128, 0, 0]) if static else np.array([0, 128, 0])
        self.static = static
        # self.links = []

    def draw(self, display):
        pygame.draw.circle(display, self.color, self.position, 5)
