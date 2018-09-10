from unittest import TestCase
from topology.topology_map import TopologyMap
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

    def test_get_z_unknown_point(self):
        self.assertIsNone(self.topology_map.get_z(Point2D(3, 3)))

    def test_set_and_get_z_with_different_point_objects(self):
        self.topology_map.set_z(Point2D(3, 3), 10)
        self.assertEqual(10, self.topology_map.get_z(Point2D(3, 3)))

    def test_is_highest_of_cached_adjacent(self):
        point = Point2D(5, 3)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, 100)
        self.assertTrue(self.topology_map.is_highest_of_cached_adjacent(point))

    def test_is_highest_or_tie_cached_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, 9)
        self.assertTrue(self.topology_map.is_highest_of_cached_adjacent(point))

    def test_isnt_highest_of_cached_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.assertFalse(self.topology_map.is_highest_of_cached_adjacent(point))

    def test_isnt_highest_of_cached_adjacent_if_none_found(self):
        point = Point2D(12, 11)
        clear = Point2D(11, 11)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(clear, None)
        self.assertFalse(self.topology_map.is_highest_of_cached_adjacent(point))

    def test_isnt_highest_if_point_not_found(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        self.topology_map.set_z(point, None)
        self.assertFalse(self.topology_map.is_highest_of_cached_adjacent(point))


if __name__ == '__main__':
    unittest.main()
