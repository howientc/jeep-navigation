#!/usr/bin/python3
#  -*- coding: utf-8 -*-
"""
Illustrates the basic usage of the library
"""

# Sets the python path first in case PYTHONPATH isn't correct
import sys
sys.path.extend(['.', './src', './tests', './examples'])

from drone.drone_factory import DroneFactory
from geometry.point import Point2D
from navigation.destinations import ExtractionPoint
from navigation.move_strategy import MoveStrategyType
from sensors.simulated_topology_sensor import SimulatedTopologySensor
from topology.topology_factory import TopologyFactory
import random
SIMULATED_MAP_DIMENSIONS = Point2D(48, 32)


def navigate_to_extraction_point(start_point):
    """
    Calculates the extraction point on a simulated map given a start point
    :param start_point: Point2D
    :return: extraction Point2D
    """
    # Generate a fake topology for testing. Higher density=more bumpy
    simulated_topology = TopologyFactory.make_fake_topology(upper_right=SIMULATED_MAP_DIMENSIONS, density=0.0075)

    # Make a sensor which scans a siulated topology
    topology_sensors = [SimulatedTopologySensor(simulated_map=simulated_topology, power_on_cost=4, scan_point_cost=2)]

    strategy = MoveStrategyType.BINARY_SEARCH
    destination = ExtractionPoint()

    drone = DroneFactory.make_drone(move_strategy=MoveStrategyType.BINARY_SEARCH,
                            topology_sensors=topology_sensors,
                            destination=ExtractionPoint())

    path = drone.navigate_to_destination_point(start_point)
    return path[-1]  # last element is our destination


if __name__ == '__main__':
    random.seed(1)  # so we always get same result, we can set a seed
    beacon_point = Point2D(15, 25)
    extraction_point = navigate_to_extraction_point(beacon_point)
    print('Navigated from {} to {}'.format(beacon_point, extraction_point.to_2d()))
