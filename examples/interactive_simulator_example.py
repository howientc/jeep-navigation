#!/usr/bin/python3
#  -*- coding: utf-8 -*-
# Sets the python path first in case PYTHONPATH isn't correct
import sys
sys.path.extend(['.', './src', './tests', './examples'])

from geometry.point import Point2D
from drone.drone_factory import DroneFactory
from navigation.move_strategy import MoveStrategyType, make_move_strategy
from sensors.simulated_topology_sensor import SimulatedTopologySensor

from plot_topology_map import plot_topology_map
from tests.topology.topology_factory import TopologyFactory
# import random

strategies = [
              MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL,
              MoveStrategyType.CLIMB_MOVE_1,
              MoveStrategyType.BINARY_SEARCH,
              # MoveStrategyType.SPIRAL_OUT_CW_3
              ]


class InteractiveSimulatorExample(object):
    def __init__(self):
        # random.seed(100)  # for testing, we want to always genereate same map
        self.tm = TopologyFactory.make_fake_topology(upper_right=Point2D(48, 32), density=0.0075)
        laser = SimulatedTopologySensor(simulated_map=self.tm, power_on_cost=4, scan_point_cost=2)
        # radar = SimulatedTopologySensor(simulated_map=self.tm, power_on_cost=10, scan_point_cost=0)
        topology_sensors = [laser]
        self.strategy_index = 0
        self.move_strategy = strategies[self.strategy_index]
        self.drone = DroneFactory.make_drone(move_strategy=self.move_strategy,
                                             topology_sensors=topology_sensors)
        self.last_xy = None

    def strategy_change(self):
        self.strategy_index = (self.strategy_index + 1) % len(strategies)
        self.move_strategy = strategies[self.strategy_index]

    def navigate(self, x, y, change_strategy=False):
        if change_strategy:
            if not self.last_xy:
                return None
            (x, y) = self.last_xy
        else:
            self.last_xy = (x, y)

        nav = self.drone.navigator
        if change_strategy:
            self.strategy_change()

        nav.set_move_strategy(make_move_strategy(self.move_strategy))  # need to reset between runs
        path = list(self.drone.navigate_to_destination_point(Point2D(x, y)))
        points = [(pt.x, pt.y, pt.z, nav.get_scan_cost_at_point(pt)) for pt in
                  path]  # convert from Point3D list to tuple list
        return points, self.move_strategy.name

    def run(self):
        plot_topology_map(self.tm, lambda x, y, c: self.navigate(x, y, c))


if __name__ == '__main__':
    example = InteractiveSimulatorExample()
    example.run()
