import logging
from unittest import TestCase
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.topology_factory import TopologyFactory
from geometry.point import Point2D
from drone.drone_factory import DroneFactory
from navigation.move_strategy import MoveStrategyType


class TestDrone(TestCase):
    def setUp(self):
        simulated_topology_map = TopologyFactory.make_fake_topology()
        topology_sensors = [SimulatedTopologySensor(simulated_topology_map)]
        self.drone = DroneFactory.make_drone(move_strategy=MoveStrategyType.NAIVE_MOVE_ONE,
                                             topology_sensors=topology_sensors)

    def test_navigate(self):
        logging.getLogger().setLevel(level=logging.INFO)
        self.drone.navigate_to_extraction_point(Point2D(10, 10))

