import configparser

import pygame

import math
import time
import sys
from RRT import RRTGraph, BuildEnv
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

