import unittest
import copy
import pprint
from collections import defaultdict
from geometry.point import Point
from topology import Topology


class Jeep(object):
    def __init__(self, topology_sensor):
        self.topology_sensor = topology_sensor


    def navigate_to_extraction_point(self, start_point):
        point = copy.copy(start_point) # don't mutate the input in case it's used elsewhere
        while True:
            move = self._get_movement(point)
            if move == (0, 0):
                return point
            point.offset_x_y(move)

    def _get_movement(self, point):
        """

        :param point:
        :return: a tuple (x,y) that indicates the offset we should move to. A value of (0,0) means we're at
        a high point, so no need to move (we're done)
        """
        adjacent = self.topology_sensor.get_adjacent_toplogy(point)
        print(point)
        print(adjacent)
        biggest = adjacent[1][1] # initially set to home square
        offset_x_y = (0, 0)
        # now find any value bigger than the home square
        for y in range(3):
            for x in range(3):
                if adjacent[y][x] > biggest:
                    biggest = adjacent[y][x]
                    offset_x_y = (y -1, x -1) # subtracting one to get a range of -1 to +1
        return offset_x_y
