import math
import pygame
import numpy as np
from tools import Coordinate, RGB
from configparser import ConfigParser

class Robot:
    def __init__(self, pos: Coordinate, robot_img_path: str, map: pygame.Surface):
        self.m2p = 3779.52  # метры в пиксели
        self.map = map

        self.pos = pos
        self.path = None
        self.w = 0.001 * self.m2p
        self.u = 0
        self.theta = 0
        self.a = 0.01 * self.m2p
        self.maxspeed = 0.02 * self.m2p
        self.waypoint = None

        # gfx
        self.img = pygame.image.load(robot_img_path)
        self.img = pygame.transform.scale(self.img, (60, 58))
        self.rotated = self.img
        self.rect = self.rotated.get_rect(center=(self.pos.x, self.pos.y))

    def draw(self) -> None:
        self.map.blit(self.rotated, self.rect)

    def check_path(self, path) -> None:
        if len(path):
            self.path = path
            self.waypoint = len(path) - 1

    def dist(self, coord) -> float:
        px = (coord[0] - self.pos.x) ** 2
        py = (coord[1] - self.pos.y) ** 2
        return math.sqrt(px + py)

    def follow_path(self) -> None:
        target = self.path[self.waypoint]
        delta_x = target[0] - self.pos.x
        delta_y = target[1] - self.pos.y
        self.u = delta_x * math.cos(self.theta) + delta_y * math.sin(self.theta)
        self.w = (-1 / self.a) * math.sin(self.theta) * delta_x + (1 / self.a) * math.cos(self.theta) * delta_y

        if self.dist(self.path[self.waypoint]) <= 35:
            self.waypoint -= 1

        if self.waypoint <= 0:
            self.waypoint = 0

    def move(self, dt) -> None:
        self.pos.x += (self.u * math.cos(self.theta) - self.a * math.sin(self.theta) * self.w) * dt
        self.pos.y += (self.u * math.sin(self.theta) + self.a * math.cos(self.theta) * self.w) * dt
        self.theta += self.w * dt
        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(-self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.pos.x, self.pos.y))
        self.follow_path()


class LaserSensor:
    def __init__(self, map: pygame.Surface,
                 config: ConfigParser):
        self.sensor_range = config.getint('Sensor', 'sensor_range')
        self.sensor_angle = math.radians(config.getint('Sensor', 'sensor_angle'))
        self.sensor_sampling = config.getint('Sensor', 'sensor_sampling')
        self.map = map
        self.width, self.height = pygame.display.get_surface().get_size()

        # Position
        self.sensor_pos = Coordinate(0, 0)
        self.sensor_heading = 0

        # Colors
        self.black = RGB.hex2rgb(config.get('Colors', 'black'))
        self.obstacle_color = RGB.hex2rgb(config.get('Colors', 'obstacle_color'))
        self.sensor_color = RGB.hex2rgb(config.get('Colors', 'sensor_color'))

        self.obstacles = []
        self.obs_radius = config.getint('Sensor', 'obstacle_radius')

    def sense_obstacles(self, robot_pos: Coordinate, robot_angle: float):
        # Robot position
        x_r, y_r = robot_pos

        # Sensor position
        x_s = x_r + self.sensor_pos.x
        y_s = y_r + self.sensor_pos.y
        sensor_angle = robot_angle + self.sensor_heading

        start_angle = sensor_angle - self.sensor_angle
        finish_angle = sensor_angle + self.sensor_angle

        for angle in np.linspace(start_angle, finish_angle, self.sensor_sampling, False):
            x_s2 = x_s + self.sensor_range * math.cos(angle)
            y_s2 = y_s - self.sensor_range * math.sin(angle)

            for i in range(0, 100):
                u = i / 100
                x = int(x_s2 * u + x_s * (1 - u))
                y = int(y_s2 * u + y_s * (1 - u))

                if 0 < x < self.width and 0 < y < self.height:

                    color = self.map.get_at((x, y))
                    self.map.set_at((x, y), self.sensor_color)

                    # obstacle color is black
                    if (color[0], color[1], color[2]) == self.black and \
                            (color[0], color[1], color[2]) != self.obstacle_color:
                        self.obstacles.append((x, y))
                        break

    def draw_points(self):
        for coords in self.obstacles:
            pygame.draw.circle(self.map, self.obstacle_color, coords, self.obs_radius)
