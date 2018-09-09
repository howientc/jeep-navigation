import unittest
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.test_simulated_topology import TEST_MAP
from tests.topology.simulated_topology import SimulatedTopology
from topology.topology_map import TopologyMap
from geometry.point2d import Point2D

X = SimulatedTopology.OUT_OF_BOUNDS  # For convenience in test comparisons, just call it X


class TestSimulatedTopologySensor(unittest.TestCase):
    """
    Remember that in the test cases, the expected matrices must be flipped because
    increasing row means decreasing Y
    """

    def setUp(self):
        topology = SimulatedTopology(TEST_MAP)
        self.sensor = SimulatedTopologySensor(topology, topology_map=TopologyMap())

    def test_normal(self):
        self.assertEqual([[1, 1, 2], [1, 2, 3], [1, 2, 2]],
                         self.sensor.get_adjacent_topology(Point2D(1, 2)).matrix)

    def test_off_top_left(self):
        self.assertEqual([[X, 1, 2], [X, 1, 1], [X, X, X]],
                         self.sensor.get_adjacent_topology(Point2D(0, 5)).matrix)

    def test_off_bottom_right(self):
        self.assertEqual([[X, X, X], [1, 2, X], [1, 1, X]],
                         self.sensor.get_adjacent_topology(Point2D(6, 0)).matrix)


if __name__ == '__main__':
    unittest.main()
