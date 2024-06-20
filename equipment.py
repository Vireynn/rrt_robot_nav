import math

import pygame

from coordinate import Coordinate

class Robot:
    def __init__(self, pos: Coordinate, robot_img_path: str, width: float, map: pygame.Surface):
        self.m2p = 3779.52  # метры в пиксели
        self.map = map

        self.x, self.y = pos
        self.path = None
        self.w = width
        self.u = 0
        self.theta = 0
        self.a = 0.01 * self.m2p
        self.maxspeed = 0.02 * self.m2p
        self.waypoint = None

        # gfx
        self.img = pygame.image.load(robot_img_path)
        self.img = pygame.transform.scale(self.img, (60, 58))
        self.rotated = self.img
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def draw(self):
        self.map.blit(self.rotated, self.rect)

    def check_path(self, path):
        if len(path):
            self.path = path
            self.waypoint = len(path) - 1

    def dist(self, coord):
        px = (coord[0] - self.x) ** 2
        py = (coord[1] - self.y) ** 2
        return math.sqrt(px + py)

    def follow_path(self):
        target = self.path[self.waypoint]
        delta_x = target[0] - self.x
        delta_y = target[1] - self.y
        self.u = delta_x * math.cos(self.theta) + delta_y * math.sin(self.theta)
        self.w = (-1 / self.a) * math.sin(self.theta) * delta_x + (1 / self.a) * math.cos(self.theta) * delta_y

        if self.dist(self.path[self.waypoint]) <= 35:
            self.waypoint -= 1

        if self.waypoint <= 0:
            self.waypoint = 0

    def move(self, dt):
        self.x += (self.u * math.cos(self.theta) - self.a * math.sin(self.theta) * self.w) * dt
        self.y += (self.u * math.sin(self.theta) + self.a * math.cos(self.theta) * self.w) * dt
        self.theta += self.w * dt
        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(-self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
        self.follow_path()