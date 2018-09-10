from unittest import TestCase
from topology.topology_map import TopologyMap, cells_in_radius, adjacent_cells_in_radius
from geometry.point2d import Point2D


class TestTopologyMap(TestCase):

    def setUp(self):
        self.topology_map = TopologyMap()

    def create_adjacent_data_at_point(self, point):
        val = 0
        # makes a 2d array values 1-9
        for y in range(point.y - 1, point.y + 2):
            for x in range(point.x - 1, point.x + 2):
                val += 1
                self.topology_map.set_z(Point2D(x, y), val)

    def test_cells_in_radius(self):
        expecting = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        self.assertEqual(expecting, list(cells_in_radius(1)))

    def test_adjacent_cells_in_radius(self):
        expecting = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        self.assertEqual(expecting, list(adjacent_cells_in_radius(1)))

    def test_get_z_unknown_point(self):
        self.assertIsNone(self.topology_map.get_z(Point2D(3, 3)))

    def test_set_and_get_z_with_different_point_objects(self):
        self.topology_map.set_z(Point2D(3, 3), 10)
        self.assertEqual(10, self.topology_map.get_z(Point2D(3, 3)))

    def test_is_highest_of_known_adjacent(self):
        point = Point2D(5, 3)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, 100)
        self.assertTrue(self.topology_map.is_highest_of_known_adjacent(point))

    def test_is_highest_or_tie_known_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, 9)
        self.assertTrue(self.topology_map.is_highest_of_known_adjacent(point))

    def test_isnt_highest_of_known_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.assertFalse(self.topology_map.is_highest_of_known_adjacent(point))

    def test_isnt_highest_of_known_adjacent_if_none_found(self):
        point = Point2D(12, 11)
        clear = Point2D(11, 11)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(clear, None)
        self.assertFalse(self.topology_map.is_highest_of_known_adjacent(point))

    def test_isnt_highest_if_point_not_found(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, None)
        self.assertFalse(self.topology_map.is_highest_of_known_adjacent(point))

    def test_count_unknown_points_at_and_adjacent_to_fully_known_point(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        self.assertEqual(0, self.topology_map.count_unknown_points_at_and_adjacent_to_point(point))

    def test_count_unknown_points_at_and_adjacent_to_fully_unknown_point(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        way_out_there = Point2D(100, 100)
        self.assertEqual(9, self.topology_map.count_unknown_points_at_and_adjacent_to_point(way_out_there))

    def test_count_unknown_points_at_and_adjacent_to_point_where_some_unknown(self):
        # Try moving one cell over. This would mean that 3 cells are now unknown
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        point_next_door = Point2D(12, 12)
        self.assertEqual(3, self.topology_map.count_unknown_points_at_and_adjacent_to_point(point_next_door))

    def test_get_highest_adjacent_points_as_directions_just_one(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point.translate(-1, -1), 99)
        candidates = self.topology_map.get_highest_adjacent_points_as_directions(point)
        self.assertEqual([(-1, -1)], candidates)

    def test_get_highest_adjacent_points_as_directions_two(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point.translate(-1, -1), 99)
        self.topology_map.set_z(point.translate(0, -1), 99)
        candidates = self.topology_map.get_highest_adjacent_points_as_directions(point)
        self.assertEqual([(-1, -1), (0, -1)], candidates)

    def test_get_highest_adjacent_points_as_directions_three(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point.translate(-1, -1), 99)
        self.topology_map.set_z(point.translate(0, -1), 99)
        self.topology_map.set_z(point.translate(1, -1), 99)
        candidates = self.topology_map.get_highest_adjacent_points_as_directions(point)
        self.assertEqual([(-1, -1), (0, -1), (1, -1)], candidates)
