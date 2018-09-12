import unittest
from _tests.topology.test_topology_map import make_example_topology
from topology_map import TopologyMap
# from _tests.sensors.simulated_topology_sensor import SimulatedTopologySensor


class TestMoveStrategy(unittest.TestCase):
    def setUp(self):
        topology = make_example_topology()
        # sensor = SimulatedTopologySensor(topology)
        # self.strategy = MoveOneStrategy()

    def test_example(self):
        # result = self.strategy.navigate_to_extraction_point(Point2D(2, 1))
        # self.assertTrue(Point2D(6, 1), result)
        self.fail()
