import unittest
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from tests.topology.topology_factory import TopologyFactory
from topology.topology_map import OUT_OF_BOUNDS
from geometry.point import Point2D

X = OUT_OF_BOUNDS  # For convenience in test comparisons, just call it X


class TestSimulatedTopologySensor(unittest.TestCase):
    """
    Remember that in the test cases, the expected matrices must be flipped because
    increasing row means decreasing Y
    """

    def setUp(self):
        simulated_map = TopologyFactory.make_from_matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
        self.sensor = SimulatedTopologySensor(simulated_map, power_on_cost=10, scan_point_cost=2)

    def test_scan_points(self):
        """
        Just one test because it's trivial. Try scanning a row, with values out of bounds on both sides
        :return:
        """
        home_point = Point2D(0, 1)  # value is 5 at row 1 column 0
        offsets = [(-1, 0), (0, 0), (1, 0), (100, 100)]
        expecting = [(-1, 0, X, Point2D(-1, 1)), (0, 0, 5, Point2D(0, 1)), (1, 0, 6, Point2D(1, 1)),
                     (100, 100, X, Point2D(100, 101))]
        scan_results, scan_cost = self.sensor.scan_points(offsets, home_point)
        self.assertEqual(expecting, scan_results)

    def test_scan_cost(self):
        home_point = Point2D(0, 1)  # value is 5 at row 1 column 0
        offsets = [(-1, 0), (0, 0), (1, 0), (100, 100)]
        _, scan_cost = self.sensor.scan_points(offsets, home_point)

    def test_scan_total_cost(self):
        home_point = Point2D(0, 1)  # value is 5 at row 1 column 0
        offsets = [(-1, 0), (0, 0), (1, 0), (100, 100)]
        self.sensor.scan_points(offsets, home_point)
        self.sensor.scan_points(offsets, home_point)
        self.assertEqual(16, self.sensor._total_cost)

    def test_scan_point_count(self):
        home_point = Point2D(0, 1)  # value is 5 at row 1 column 0
        offsets = [(-1, 0), (0, 0), (1, 0), (100, 100)]
        self.sensor.scan_points(offsets, home_point)
        self.sensor.scan_points(offsets, home_point)
        self.assertEqual(8, self.sensor._scan_point_count)
