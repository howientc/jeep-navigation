# -*- coding: utf-8 -*-
import random
from unittest import TestCase
import logging
from drone.drone_factory import DroneFactory
from drone.drone import Drone
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.topology_factory import TopologyFactory
from geometry.point import Point2D
from navigation.move_strategy import MoveStrategyType
from pydispatch import dispatcher


class TestDrone(TestCase):
    # suppress incorrect warnings about __get__ calls below
    # noinspection PyUnresolvedReferences
    def setUp(self):
        self.tm = TopologyFactory.make_fake_topology()
        topology_sensors = [SimulatedTopologySensor(self.tm)]
        self.drone = DroneFactory.make_drone(move_strategy=MoveStrategyType.CLIMB_MOVE_1,
                                             topology_sensors=topology_sensors)

        dispatcher.connect(self.on_drone_start.__get__(self, TestDrone), signal=Drone.SIGNAL_START)
        dispatcher.connect(self.on_drone_moved.__get__(self, TestDrone), signal=Drone.SIGNAL_MOVED)
        dispatcher.connect(self.on_drone_destination.__get__(self, TestDrone), signal=Drone.SIGNAL_DESTINATION)

        self.start = []
        self.moved = []
        self.destination = []

    def on_drone_start(self, pt):
        self.start.append(pt)

    def on_drone_moved(self, pt):
        self.moved.append(pt)

    def on_drone_destination(self, pt):
        self.destination.append(pt)

    def xtest_navigate(self):
        """
        System test. Tests if navigation completes, and signals are broadcast and received
        :return:
        """
        logging.getLogger().setLevel(level=logging.INFO)

        self.drone.navigate_to_destination_point(Point2D(10, 10))
        self.assertEqual(1, len(self.start))
        self.assertEqual(1, len(self.destination))
        extraction_point = self.destination[0].to_2d()
        self.assertTrue(self.tm.is_highest_or_tie_in_radius_and_all_known(extraction_point, 1))

    def navigate(self, x, y):
        self.drone.navigate_to_destination_point(Point2D(x, y))
        path = self.drone.navigator.path
        points = [pt.to_tuple() for pt in path]  # convert from Point3D list to tuple list
        print("Found destination at", path[-1])
        print(*points)
        return points

    def test_smart(self):
        random.seed(100)  # for testing, we want to always genereate same map
        self.tm = TopologyFactory.make_fake_topology(upper_right=Point2D(20, 20))

        topology_sensors = [SimulatedTopologySensor(self.tm)]
        # move_strategy = MoveStrategyType.CLIMB_MOVE_1
        move_strategy = MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL
        # move_strategy = MoveStrategyType.SPIRAL_OUT_CW
        self.drone = DroneFactory.make_drone(move_strategy=move_strategy,
                                             topology_sensors=topology_sensors)
        self.navigate(20, 19)
