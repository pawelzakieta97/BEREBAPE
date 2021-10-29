import random
from typing import List

import pygame
import numpy as np

from link import Link
from point import Point
from numba import jit

class Simulator:
    def __init__(self):
        self.points: List[Point] = []
        self.links = []
        self.elastic_links = []
        self.g = 0
        self.constraints = []

    def get_gravity_vector(self):
        return np.array([0, 1], dtype=np.float64) * self.g

    def add_point(self, point: Point):
        self.points.append(point)

    def link(self, p1, p2, k=0):
        new_link = Link(p1, p2, k)
        self.links.append(new_link)
        # p1.links.append(new_link)
        # p2.links.append(new_link)

    def draw(self, display):
        for link in self.links:
            link.draw(display)
        for point in self.points:
            point.draw(display)

    def apply_gravity(self, dt=1/60):
        for point in self.points:
            point.position[1] += self.g * dt * dt

    def apply_gravity2(self):
        for point in self.points:
            point.applied_force += self.get_gravity_vector() * point.mass

    def apply_movement(self):
        for point in self.points:
            tmp = point.position.copy()
            point.position += point.position - point.prev_position
            point.prev_position = tmp
            point.velocity = point.position - point.prev_position
    #
    # def apply_constraints(self):
    #     iterations = 10
    #     for link in self.links:
    #         if link.k:
    #             current_length = np.linalg.norm(link.p1.position-link.p2.position)
    #             if not link.p2.static:
    #                 link.p2.position += (link.p1.position - link.p2.position)/current_length * (current_length-link.length) * link.k
    #             if not link.p1.static:
    #                 link.p1.position += (link.p2.position - link.p1.position)/current_length * (current_length-link.length) * link.k
    #
    #     for i in range(iterations):
    #         for link in self.links:
    #             if link.k == 0:
    #                 center = (link.p1.position + link.p2.position)/2
    #                 current_length = np.linalg.norm(link.p1.position-link.p2.position)
    #                 if link.p1.static and not link.p2.static:
    #                     link.p2.position = link.p1.position + (link.p2.position - link.p1.position) * link.length / current_length
    #                 if not link.p1.static and link.p2.static:
    #                     link.p1.position = link.p2.position + (link.p1.position - link.p2.position) * link.length / current_length
    #                 else:
    #                     link.p1.position = center + (link.p1.position - center) * link.length / current_length
    #                     link.p2.position = center + (
    #                                 link.p2.position - center) * link.length / current_length
    #         for point in self.points:
    #             if point.static:
    #                 point.position = point.prev_postition
    #
    # def solve(self, dt, iterations=10):
    #     for i in range(iterations):
    #         for point in self.points:
    #             if point.static:
    #                 continue
    #             point.velocity = point.prev_velocity + point.applied_force * dt / point.mass
    #             point.position = point.prev_position + (point.prev_velocity + point.velocity)/2 * dt
    #             # point.position[1] = min(point.position[1], 400)
    #             point.applied_force = self.get_applied_force(point)
    #
    #     for point in self.points:
    #         # if point.position[1] >= 400:
    #         #     point.position[1] = 400
    #         #     point.velocity[1] = (400 - point.prev_position[1]) / dt
    #         point.prev_velocity = point.velocity
    #         point.prev_position = point.position
    #
    # def solve2(self, dt, iterations=10):
    #     for i in range(iterations):
    #         for point in self.points:
    #             point.applied_force *= 0
    #         self.apply_gravity2()
    #         # random.shuffle(self.links)
    #         for link in self.links:
    #             if link.k != 0:
    #                 p1_force = link.get_force(link.p1)
    #                 p2_force = -p1_force
    #                 link.p1.applied_force += p1_force
    #                 link.p2.applied_force += p2_force
    #             else:
    #                 p1_next_vel = np.array([0, 0]) if link.p1.static else link.p1.prev_velocity + link.p1.applied_force * dt / link.p1.mass
    #                 p2_next_vel = np.array([0, 0]) if link.p2.static else link.p2.prev_velocity + link.p2.applied_force * dt / link.p2.mass
    #                 p1_next_pos = link.p1.prev_position + p1_next_vel * dt
    #                 p2_next_pos = link.p2.prev_position + p2_next_vel * dt
    #                 distance = np.linalg.norm(p2_next_pos-p1_next_pos)
    #                 required_contracting_velocity = (distance - link.length)/dt
    #                 link.tension = required_contracting_velocity/(1/link.p1.mass + 1/link.p2.mass)/dt
    #                 link.p1.applied_force += link.get_force(link.p1)
    #                 link.p2.applied_force += link.get_force(link.p2)
    #
    #         for point in self.points:
    #             if point.static:
    #                 continue
    #             for constraint in self.constraints:
    #                 constraint(point, dt=dt)
    #             point.velocity = point.prev_velocity + point.applied_force * dt / point.mass
    #             # point.position = point.prev_position + (point.prev_velocity + point.velocity)/2 * dt
    #             point.position = point.prev_position + point.velocity * dt
    #
    #     for point in self.points:
    #         point.velocity = (point.position-point.prev_position)/dt
    #         point.prev_velocity = point.velocity
    #         point.prev_position = point.position

    # @jit(nopython=True)
    def solve3(self, dt, iterations=100):
        for point in self.points:
            point.delta = None
        for i in range(iterations):
            for point in self.points:
                point.applied_force *= 0
            self.apply_gravity2()
            # random.shuffle(self.links)
            for link in self.links:
                p1_force = link.get_force(link.p1)
                p2_force = -p1_force
                link.p1.applied_force += p1_force
                link.p2.applied_force += p2_force

            for point in self.points:
                if point.static:
                    continue
                for constraint in self.constraints:
                    constraint(point, dt=dt)
                point.velocity = point.prev_velocity + point.applied_force * dt / point.mass
                # point.position = point.prev_position + (point.prev_velocity + point.velocity)/2 * dt
                point.position = point.prev_position + point.velocity * dt

        for point in self.points:
            point.velocity = (point.position-point.prev_position)/dt
            point.prev_velocity = point.velocity
            point.prev_position = point.position
    #
    #
    # def get_applied_force(self, p: Point):
    #     force = np.array([0, 0], dtype=np.float64)
    #     for link in p.links:
    #         force += link.get_force(p)
    #     force += np.array([0, 1], dtype=np.float64) * self.g * p.mass
    #     return force
    #
    # def step(self, dt):
    #     self.apply_gravity(dt)
    #     self.apply_constraints()
    #     self.apply_movement()
    #
    # def step2(self, dt):
    #     self.solve2(dt)

    def step3(self, dt):
        self.solve3(dt)

pygame.init()
window = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
sim = Simulator()
p1 = Point([200, 100], static=False, mass=1)
p2 = Point([300, 100], static=True, mass=1)
p3 = Point([250, 200], static=False, mass=1)
# p4 = Point([350, 200], static=False, mass=1)
# sim.add_point(p1)
# sim.add_point(p2)
# sim.add_point(p3)
# # sim.add_point(p4)
# sim.link(p1, p2)
# sim.link(p2, p3)
# sim.link(p1, p3)
# p3.position += np.array([150, 0])
# sim.link(p3, p4)
# sim.link(p2, p4)
# sim.g=300

def floor_constraint(point: Point, bounciness=0.5, dt=1/60):
    if point.position[1] > 500:
        next_vel = np.array(
            [0, 0]) if point.static else point.prev_velocity + point.applied_force * dt / point.mass
        required_upward_vel = abs(next_vel[1])
        required_reaction_force = required_upward_vel/dt * point.mass
        point.applied_force[1] = point.applied_force[1] - required_reaction_force
        # point.position[1] = 500
        # point.velocity[1] = -bounciness * point.velocity[1]
sim.constraints.append(floor_constraint)

run = True
last_point = None
first_point = None
k = 0
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                new_point = None
                min_distance = 10
                for point in sim.points:
                    distance = np.linalg.norm(np.array(event.pos) - point.position)
                    if distance < min_distance:
                        min_distance = distance
                        new_point = point
                new_point = new_point or Point(event.pos, static=False)
            else:
                new_point = Point(event.pos, static=True)
            if first_point is None:
                first_point = new_point
            if new_point not in sim.points:
                sim.add_point(new_point)
            if last_point is not None:
                sim.link(last_point, new_point, k)
            last_point = new_point
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sim.g = 300 if sim.g == 0 else 0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            k = 50 if k == 0 else 0

        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            last_point = None
            first_point = None

    window.fill((255, 255, 255))
    sim.step3(1/60)
    sim.draw(window)
    pygame.display.flip()

pygame.quit()
exit()