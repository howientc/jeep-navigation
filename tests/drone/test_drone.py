from unittest import TestCase
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.simulate_topology import SimulatedTopology
from tests.topology.test_topology_map import TEST_MAP
from geometry.point2d import Point2D
from drone.drone_factory import DroneFactory
from navigation.move_strategy import MoveStrategyType


class TestDrone(TestCase):
    def setUp(self):
        simulated_topology_map = SimulatedTopology(TEST_MAP)
        topology_sensors = [SimulatedTopologySensor(simulated_topology_map)]
        self.drone = DroneFactory.make_drone(move_strategy=MoveStrategyType.NAIVE_MOVE_ONE,
                                             topology_sensors=topology_sensors)

    def test_navigate(self):
        extraction_point = self.drone.iter_points_to_destination(Point2D(2, 2))
