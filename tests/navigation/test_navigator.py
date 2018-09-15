# -*- coding: utf-8 -*-
from unittest import TestCase
from tests.sensors.simulated_topology_sensor import SimulatedTopologySensor
from navigation.navigator import Navigator
from topology.topology_map import TopologyMap
from tests.topology.test_topology_map import make_example_topology
from navigation.navigator_factory import NavigatorFactory
from navigation.move_strategy import make_move_strategy, MoveStrategyType
from geometry.point import Point2D, Point3D
from navigation.destinations import ExtractionPoint


# TEST_MAP = [
# #    0  1  2  3  4  5  6
#     [1, 1, 1, 1, 1, 1, 1],  # 5
#     [1, 2, 2, 1, 1, 2, 4],  # 4
#     [1, 2, 2, 2, 1, 2, 2],  # 3
#     [1, 2, 3, 2, 1, 1, 1],  # 2
#     [1, 1, 2, 1, 1, 1, 1],  # 1
#     [1, 1, 1, 1, 1, 1, 2],  # 0
# ]

def to_points(list_of_points):
    return [Point2D(x, y) for (x, y) in list_of_points]


#
# for adj_point in tm.unknown_offsets_in_radius(scanned_pt):
#     candidates.add(adj_point)  # if might already be in thereif it was in scanned, which is fine

class TestNavigator(TestCase):
    def setUp(self):
        simulated_map = make_example_topology()
        # simulated_map = TopologyFactory.make_fake_topology()
        self.laser = SimulatedTopologySensor(simulated_map=simulated_map, power_on_cost=4, scan_point_cost=2)
        self.radar = SimulatedTopologySensor(simulated_map=simulated_map, power_on_cost=10, scan_point_cost=0)
        self.sensors = [self.laser, self.radar]
        move_strategy = make_move_strategy(MoveStrategyType.CLIMB_MOVE_1)
        tm = TopologyMap()
        self.navigator = NavigatorFactory.make_navigator(topology_map=tm,
                                                         move_strategy=move_strategy,
                                                         destination=ExtractionPoint())

    def add_points(self, list_of_points):
        for pt in to_points(list_of_points):
            self.navigator._topology_map.set_z(pt, 1)

    def test_determine_next_point(self):
        point = Point2D(4, 1)
        point = self.navigator._determine_next_point(point, self.sensors)
        expecting = Point2D(3, 2)
        self.assertEqual(expecting, point)

    def test_iter_points_to_destination(self):
        point = Point2D(4, 1)

        path = list(self.navigator.iter_points_to_destination(point, self.sensors))
        self.assertCountEqual([Point3D(4, 1, 1), Point3D(3, 2, 2), Point3D(2, 2, 3)], path)

    def test_scan_and_get_destination_point_candidates(self):
        # we should get the point, its 8 surrounding points, and for each of those 8, their surrounding points
        # the result is essentially a 5x5 grid of points centered around the origin point
        point = Point2D(4, 1)
        surround = to_points([(x, y) for y in range(-1, 4) for x in range(2, 7)])
        # xy = [(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)]
        candidates = self.navigator._scan_and_get_destination_point_candidates(point, self.sensors)
        self.assertCountEqual(surround, candidates)

    def test_choose_single_sensor(self):
        offsets = [(-1, 0), (0, 1)]
        best = Navigator.choose_best_sensor([self.laser], offsets)
        self.assertEqual(self.laser, best)

    def test_choose_best_sensor_few_points(self):
        offsets = [(-1, 0), (0, 1)]
        best = Navigator.choose_best_sensor(self.sensors, offsets)
        self.assertEqual(self.laser, best)

    def test_choose_best_sensor_many_points(self):
        offsets = [(-1, 0), (0, 1), (1, 1), (-1, -1)]
        best = Navigator.choose_best_sensor(self.sensors, offsets)
        self.assertEqual(self.radar, best)

    def test_choose_best_sensor_tie_pick_first(self):
        offsets = [(-1, 0), (0, 1), (1, 1)]
        best = Navigator.choose_best_sensor(self.sensors, offsets)
        self.assertEqual(self.laser, best)
