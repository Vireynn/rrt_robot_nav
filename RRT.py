from configparser import ConfigParser
from tools import Coordinate, RGB
import random
import math
import time
import pygame

class BuildEnv:
    def __init__(self, config: ConfigParser):
        # Pygame initialization
        pygame.init()

        # Map params
        self.map_path = config.get('Filepath', 'map_path')
        self.mapw = config.getfloat('Screen', 'width')
        self.maph = config.getfloat('Screen', 'height')
        self.window_name = config.get('Screen', 'window_name')

        self.external_map = pygame.image.load(self.map_path)
        pygame.display.set_caption(self.window_name)
        self.map = pygame.display.set_mode((self.mapw, self.maph))
        self.map.blit(self.external_map, (0, 0))

        # colors
        self.black = RGB.hex2rgb(config.get('Colors', 'black'))
        self.white = RGB.hex2rgb(config.get('Colors', 'white'))
        self.red = RGB.hex2rgb(config.get('Colors', 'red'))
        self.green = RGB.hex2rgb(config.get('Colors', 'green'))
        self.blue = RGB.hex2rgb(config.get('Colors', 'blue'))

        # Other settings
        self.nodeRad = 2
        self.level = 0
        self.start_pos: Coordinate | None = None
        self.finish_pos: Coordinate | None = None

        self.edgeThickness = 1

    def update_screen(self):
        self.map.blit(self.external_map, (0, 0))

    def get_start_pos(self):
        m = pygame.mouse.get_pressed()
        x, y = pygame.mouse.get_pos()

        if m[0] == 1:
            match self.level:
                case 0:
                    pygame.draw.circle(self.map, self.red, [x, y], self.nodeRad + 5, 0)
                    self.start_pos = Coordinate(x, y)
                    self.level += 1
                case 1:
                    pygame.draw.circle(self.map, self.green, [x, y], self.nodeRad + 5, 0)
                    self.finish_pos = Coordinate(x, y)
                    self.level = None

    def drawPath(self, path: list):
        for node in path:
            pygame.draw.circle(self.map, self.red, node, 3, 0)


class RRTGraph:
    def __init__(self, start: Coordinate,
                 goal: Coordinate,
                 MapDimensions: tuple[int, int],
                 screen: pygame.Surface,
                 config: ConfigParser):

        x, y = start
        self.screen = screen
        self.start = start
        self.goal = goal
        self.goalFlag = False
        self.mapw, self.maph = MapDimensions
        self.x = []
        self.y = []
        self.parent = []

        # initialize the tree
        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)

        # path
        self.goalstate = None
        self.path = []

        # colors
        self.obstacle_color = RGB.hex2rgb(config.get('Colors', 'obstacle_color'))

    def add_node(self, n, x, y) -> None:
        self.x.insert(n, x)
        self.y.append(y)

    def remove_node(self, n: int) -> None:
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self, parent, child) -> None:
        self.parent.insert(child, parent)

    def remove_edge(self, n: int) -> None:
        self.parent.pop(n)

    def number_of_nodes(self) -> int:
        return len(self.x)

    def distance(self, n1: int, n2: int) -> float:
        x1, y1 = (self.x[n1], self.y[n1])
        x2, y2 = (self.x[n2], self.y[n2])
        px = (float(x1) - float(x2)) ** 2
        py = (float(y1) - float(y2)) ** 2
        return (px + py) ** 0.5

    def sample_envir(self):
        x = int(random.uniform(0, self.mapw))
        y = int(random.uniform(0, self.maph))
        return x, y

    def nearest(self, n: int) -> int:
        dmin = self.distance(0, n)
        nnear = 0
        for i in range(0, n):
            if self.distance(i, n) < dmin:
                dmin = self.distance(i, n)
                nnear = i
        return nnear

    def isFree(self) -> bool:
        n = self.number_of_nodes() - 1
        x, y = (self.x[n], self.y[n])
        if self.screen.get_at((x, y)) == self.obstacle_color:
            self.remove_node(n)
            return False
        else:
            return True

    def crossObstacle(self, x1, x2, y1, y2) -> bool:
        for i in range(0, 101):
            u = i / 100
            x = int(x1 * u + x2 * (1 - u))
            y = int(y1 * u + y2 * (1 - u))
            if self.screen.get_at((x, y)) == self.obstacle_color:
                return True
        return False

    def connect(self, n1: int, n2: int) -> bool:
        x1, y1 = (self.x[n1], self.y[n1])
        x2, y2 = (self.x[n2], self.y[n2])
        if self.crossObstacle(x1, x2, y1, y2):
            self.remove_node(n2)
            return False
        else:
            self.add_edge(n1, n2)
            return True

    def step(self, nnear: int, nrand: int, dmax: int = 35):
        d = self.distance(nnear, nrand)
        if d > dmax:
            u = dmax / d
            (xnear, ynear) = (self.x[nnear], self.y[nnear])
            (xrand, yrand) = (self.x[nrand], self.y[nrand])
            (px, py) = (xrand - xnear, yrand - ynear)
            theta = math.atan2(py, px)

            (x, y) = (int(xnear + dmax * math.cos(theta)),
                      int(ynear + dmax * math.sin(theta)))

            self.remove_node(nrand)

            if abs(x - self.goal[0]) <= dmax and abs(y - self.goal[1]) <= dmax:
                self.add_node(nrand, self.goal[0], self.goal[1])
                self.goalstate = nrand
                self.goalFlag = True
            else:
                self.add_node(nrand, x, y)

    def bias(self, ngoal: tuple[int, int]):
        n = self.number_of_nodes()
        self.add_node(n, ngoal[0], ngoal[1])
        nnear = self.nearest(n)
        self.step(nnear, n)
        self.connect(nnear, n)
        return self.x, self.y, self.parent

    def expand(self):
        n = self.number_of_nodes()
        x, y = self.sample_envir()
        self.add_node(n, x, y)
        if self.isFree():
            xnearest = self.nearest(n)
            self.step(xnearest, n)
            self.connect(xnearest, n)
        return self.x, self.y, self.parent

    def path_to_goal(self):
        if self.goalFlag:
            self.path = []
            self.path.append(self.goalstate)
            newpos = self.parent[self.goalstate]
            while newpos != 0:
                self.path.append(newpos)
                newpos = self.parent[newpos]
            self.path.append(0)
        return self.goalFlag

    def getPathCoords(self):
        pathCoords = []
        for node in self.path:
            x, y = (self.x[node], self.y[node])
            pathCoords.append((x, y))
        return pathCoords

    def cost(self, n: int):
        n_init = 0
        parent = self.parent[n]
        c = 0
        while n is not n_init:
            c = c + self.distance(n, parent)
            n = parent
            if n is not n_init:
                parent = self.parent[n]
        return c

    def waypoints2path(self):
        oldpath = self.getPathCoords()
        path = []
        for i in range(0, len(self.path) - 1):
            if i >= len(self.path):
                break
            x1, y1 = oldpath[i]
            x2, y2 = oldpath[i + 1]
            for i in range(0, 5):
                u = i / 5
                x = int(x2 * u + x1 * (1 - u))
                y = int(y2 * u + y1 * (1 - u))
                path.append((x, y))

        return path
