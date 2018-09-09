import unittest
from navigation.move_one_strategy import MoveOneStrategy
from tests.topology.simulated_topology import SimulatedTopology
from tests.topology.test_simulated_topology import TEST_MAP
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from geometry.point2d import Point2D


class TestMoveOneStrategy(unittest.TestCase):
    def setUp(self):
        topology = SimulatedTopology(TEST_MAP)
        sensor = SimulatedTopologySensor(topology)
        self.strategy = MoveOneStrategy()

    def test_example(self):
        result = self.strategy.navigate_to_extraction_point(Point2D(2, 1))
        self.assertTrue(Point2D(6, 1), result)


if __name__ == '__main__':
    unittest.main()
