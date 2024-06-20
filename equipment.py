import math
import pygame
import numpy as np
from coordinate import Coordinate
from typing import Tuple
from configparser import ConfigParser

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


class LaserSensor:
    def __init__(self, sensor_range: Tuple[int, float],
                 map: pygame.Surface,
                 config: ConfigParser):
        self.sensor_range = sensor_range
        self.map = map
        self.width, self.height = pygame.display.get_surface().get_size()

        # Position
        self.sensor_pos = Coordinate(0, 0)
        self.sensor_heading = 0

        # Colors
        self.BLACK = (0, 0, 0)
        self.SPRING_GREEN = (0, 255, 100)
        self.FROZEN_SKY = (0, 200, 255)

        self.obstacles = []
        self.obs_radius = 20

    def sense_obstacles(self, robot_pos: Coordinate, robot_angle: float):
        # Robot position
        x_r, y_r = robot_pos

        # Sensor position
        x_s = x_r + self.sensor_pos.x
        y_s = y_r + self.sensor_pos.y
        sensor_angle = robot_angle + self.sensor_heading

        start_angle = sensor_angle - self.sensor_range[1]
        finish_angle = sensor_angle + self.sensor_range[1]

        for angle in np.linspace(start_angle, finish_angle, 30, False):
            x_s2 = x_s + self.sensor_range[0] * math.cos(angle)
            y_s2 = y_s - self.sensor_range[0] * math.sin(angle)

            for i in range(0, 100):
                u = i / 100
                x = int(x_s2 * u + x_s * (1 - u))
                y = int(y_s2 * u + y_s * (1 - u))

                if 0 < x < self.width and 0 < y < self.height:

                    color = self.map.get_at((x, y))
                    self.map.set_at((x, y), (0, 208, 255))

                    # obstacle color is black
                    if (color[0], color[1], color[2]) == self.BLACK and \
                            (color[0], color[1], color[2]) != self.SPRING_GREEN:
                        self.obstacles.append((x, y))
                        break
