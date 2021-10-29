import numpy as np
import pygame
from point import Point
import colorsys

class Link:
    def __init__(self, p1: Point, p2: Point, k=0, tension_to_color=True, strength=3000):
        self.p1 = p1
        self.p2 = p2
        self.length = np.linalg.norm(p1.position - p2.position)
        self.color = (128, 128, 128) if k == 0 else (128, 0, 0)
        self.k = k
        # contracting force (link is being stretched, wants to contract)
        self.delta = None
        self.multiplier = 0
        self.tension = None
        self.tension_to_color = tension_to_color
        self.strength = strength

    def draw(self, display):
        if self.tension_to_color:
            tension = self.tension or 0
            self.color = colorsys.hsv_to_rgb(0.33*(max(self.strength-abs(tension), 0))/self.strength, 1, 1)
            self.color = [int(255*c) for c in self.color]
        pygame.draw.line(display, self.color, self.p1.position, self.p2.position, 2)
        # print(self.tension)

    def get_force(self, p: Point):
        p1p2 = self.p2.position - self.p1.position
        current_length = np.linalg.norm(p1p2)
        force_direction = p1p2 / current_length
        # print(current_length)
        if self.k != 0:
            if self.k != 0:
                self.tension = self.k * (current_length - self.length)
                return self.tension * p1p2 / current_length if p == self.p1 else -self.tension * p1p2 / current_length
        else:
            if self.delta is None:
                self.tension = 1 if current_length > self.length else -1
                self.delta = self.tension
            if abs(self.delta) < 0.000000000000000000001:
                self.delta *= 2
            if (current_length - self.length) * self.delta > 0:
                self.tension = self.tension + self.delta
                self.delta = self.delta * 2
            else:
                self.tension = self.tension - self.delta/2
                self.delta = -self.delta/2
            return force_direction * self.tension if p == self.p1 else -force_direction * self.tension

if __name__ == '__main__':
    p1 = Point([0,0])
    p2 = Point([1,0])
    link = Link(p1, p2, k=0)
    p2.position += np.array([0.1,0])
    for i in range(10):
        print(link.get_force(p2))

