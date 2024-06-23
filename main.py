import configparser

import pygame

import math
import time
import sys
from RRT import RRTGraph, BuildEnv, pathBuilder
from equipment import Robot, LaserSensor
from tools import Coordinate

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    running = True

    map = BuildEnv(config)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif map.start_pos is not None and map.finish_pos is not None:
                running = False
                break
            map.get_start_pos()
        pygame.display.update()

    # Robot
    start_pos = Coordinate(*map.start_pos)
    robot = Robot(pos=start_pos,
                  robot_img_path=config.get('Filepath', 'robot_image'),
                  map=map.map)
    robot.draw()
    pygame.display.update()

    # Sensor
    sensor = LaserSensor(map.map, config)
    lasttime = pygame.time.get_ticks()
    step = 15
    running = False
    path = None
    t = 1
    graph = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        sensor.sense_obstacles(robot_pos=Coordinate(robot.x, robot.y),
                               robot_angle=-robot.theta)
        sensor.draw_points()
        if not running:
            graph = RRTGraph(start=Coordinate(robot.x, robot.y),
                             goal=map.finish_pos,
                             screen=map.map,
                             config=config)
            path = pathBuilder().build_path(graph, map)
            robot.check_path(path)
            running = True

        while running:
            dt = (pygame.time.get_ticks() - lasttime) / 1000
            lasttime = pygame.time.get_ticks()

            map.update_screen()
            map.drawPath(path)
            sensor.draw_points()
            robot.move(dt)
            robot.draw()
            sensor.sense_obstacles(robot_pos=Coordinate(robot.x, robot.y),
                                   robot_angle=-robot.theta)
            if robot.waypoint <= step:
                j = 0
            else:
                j = robot.waypoint - step

            path_points = path[j:robot.waypoint]
            index = len(path_points) - 1
            while index >= 0:
                x1, y1 = path_points[index]
                x2, y2 = path_points[index - 1]
                if graph.crossObstacle(x1, x2, y1, y2):
                    running = False
                    break
                index -= 1

            pygame.display.update()
            pygame.display.flip()

if __name__ == '__main__':
    main()

