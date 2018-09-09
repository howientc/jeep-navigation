from unittest import TestCase
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.simulated_topology import SimulatedTopology
from tests.topology.test_simulated_topology import TEST_MAP
from geometry.point2d import Point2D
from drone.drone_factory import DroneFactory, NavigationStrategyType


class TestDrone(TestCase):
    def setUp(self):
        simulated_topology_map = SimulatedTopology(TEST_MAP)
        topology_sensor = SimulatedTopologySensor(simulated_topology_map)

        self.drone = DroneFactory.make_drone(navigation_strategy=NavigationStrategyType.MoveOne,
                                             topology_sensor=topology_sensor)

    def test_navigate(self):
        extraction_point = self.drone.navigate_to_extraction_point(Point2D(2, 2))


