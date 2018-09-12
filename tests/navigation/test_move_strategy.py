import unittest
from tests.topology.test_topology_map import TEST_MAP
from topology_map import TopologyMap
# from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor


class TestMoveStrategy(unittest.TestCase):
    def setUp(self):
        topology = TopologyMap()
        topology.populate_from_matrix(TEST_MAP)
        # sensor = SimulatedTopologySensor(topology)
        # self.strategy = MoveOneStrategy()

    def test_example(self):
        # result = self.strategy.navigate_to_extraction_point(Point2D(2, 1))
        # self.assertTrue(Point2D(6, 1), result)
        self.fail()
