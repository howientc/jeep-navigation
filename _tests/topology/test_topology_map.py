from unittest import TestCase
from topology.topology_map import TopologyMap, iter_offsets_in_radius, iter_adjacent_offsets_in_radius, OUT_OF_BOUNDS
from geometry.point import Point2D, ORIGIN
from _tests.topology.topology_factory import TopologyFactory

TEST_MAP = [
    #    0  1  2  3  4  5  6
    [1, 1, 1, 1, 1, 1, 1],  # 5
    [1, 2, 2, 1, 1, 2, 4],  # 4
    [1, 2, 2, 2, 1, 2, 2],  # 3
    [1, 2, 3, 2, 1, 1, 1],  # 2
    [1, 1, 2, 1, 1, 1, 1],  # 1
    [1, 1, 1, 1, 1, 1, 2],  # 0
]


def make_example_topology(origin=ORIGIN, set_bounds=True):
    """
    Covenience method for other _tests to use the same example topology
    :param origin: the lower-left corner. 0,0 by default
    :param set_bounds: Whether to limit the topology to the matrix bounds
    :return: a TopologyMap based on the TEST_MAP above
    """
    return TopologyFactory.make_from_matrix(TEST_MAP, origin=origin, set_bounds=set_bounds)


class TestTopologyMap(TestCase):

    def setUp(self):
        self.tm = TopologyMap()

    def create_adjacent_data_at_point(self, point):
        val = 0
        # makes a 2d array values 1-9
        for y in range(point.y - 1, point.y + 2):
            for x in range(point.x - 1, point.x + 2):
                val += 1
                self.tm.set_z(Point2D(x, y), val)

    def test_width_and_height(self):
        self.tm.set_z(Point2D(9, 5), 1)
        self.tm.set_z(Point2D(5, 7), 5)
        self.tm.set_z(Point2D(1, 6), 2)
        # don't forget that we need to add 1 to both width and height!
        self.assertEqual((9, 3), self.tm.width_and_height)

    def test_boundary_points(self):
        self.tm.set_z(Point2D(9, 5), 1)
        self.tm.set_z(Point2D(5, 7), 5)
        self.tm.set_z(Point2D(1, 6), 2)
        self.assertEqual((Point2D(1, 5), Point2D(9, 7)), self.tm.boundary_points)

    def test_all_points_xyz(self):
        self.tm.set_z(Point2D(9, 5), 1)
        self.tm.set_z(Point2D(5, 7), 5)
        self.tm.set_z(Point2D(1, 6), 2)
        # Note assertCountEqual below actually sees if the elements are the same, regardless of order
        self.assertCountEqual([(9, 5, 1), (5, 7, 5), (1, 6, 2)], self.tm.iter_all_points_xyz())

    def test_cells_in_radius(self):
        expecting = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        self.assertEqual(expecting, list(iter_offsets_in_radius(1)))

    def test_unknown_cells_in_radius(self):
        point = Point2D(5, 5)
        self.tm.set_z(Point2D(5, 6), 1)
        expecting = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]

        unknown_adjacent_cells = self.tm.unknown_adjacent_offsets(point)
        self.assertCountEqual(expecting, unknown_adjacent_cells)

    def test_unknown_adjacent_points(self):
        """
        Gets points for all unknown points around a point.
        :param point:
        :param radius:
        :return:
        """
        point = Point2D(3, 3)
        self.tm.set_z(Point2D(3, 3), 1)
        expecting = [Point2D(x, y) for (x, y) in [(2, 2), (3, 2), (4, 2), (2, 3), (4, 3), (2, 4), (3, 4), (4, 4)]]

        unknown_adjacent_points = self.tm.unknown_adjacent_points(point)
        self.assertCountEqual(expecting, unknown_adjacent_points)

    def test_adjacent_cells_in_radius(self):
        expecting = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        self.assertEqual(expecting, list(iter_adjacent_offsets_in_radius(1)))

    def test_get_z_unknown_point(self):
        self.assertIsNone(self.tm.get_z(Point2D(3, 3)))

    def test_set_and_get_z_with_different_point_objects(self):
        self.tm.set_z(Point2D(3, 3), 10)
        self.assertEqual(10, self.tm.get_z(Point2D(3, 3)))

    def test_is_highest_of_known_adjacent(self):
        point = Point2D(5, 3)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point, 100)
        self.assertTrue(self.tm.is_highest_of_adjacent_points(point))

    def test_is_highest_or_tie_known_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point, 9)
        self.assertTrue(self.tm.is_highest_of_adjacent_points(point))

    def test_isnt_highest_of_known_adjacent(self):
        point = Point2D(8, 1)
        self.create_adjacent_data_at_point(point)
        self.assertFalse(self.tm.is_highest_of_adjacent_points(point))

    def test_isnt_highest_of_known_adjacent_if_none_found(self):
        point = Point2D(12, 11)
        clear = Point2D(11, 11)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(clear, None)
        self.assertFalse(self.tm.is_highest_of_adjacent_points(point))

    def test_isnt_highest_if_point_not_found(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point, None)
        self.assertFalse(self.tm.is_highest_of_adjacent_points(point))

    def test_count_unknown_points_at_and_adjacent_to_fully_known_point(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        self.assertEqual(0, self.tm.count_unknown_points_at_and_adjacent_to_point(point))

    def test_count_unknown_points_at_and_adjacent_to_fully_unknown_point(self):
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        way_out_there = Point2D(100, 100)
        self.assertEqual(9, self.tm.count_unknown_points_at_and_adjacent_to_point(way_out_there))

    def test_count_unknown_points_at_and_adjacent_to_point_where_some_unknown(self):
        # Try moving one cell over. This would mean that 3 cells are now unknown
        point = Point2D(12, 11)
        self.create_adjacent_data_at_point(point)
        point_next_door = Point2D(12, 12)
        self.assertEqual(3, self.tm.count_unknown_points_at_and_adjacent_to_point(point_next_door))

    def test_get_highest_adjacent_points_as_directions_just_one(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point.translate(-1, -1), 99)
        candidates = self.tm.get_highest_adjacent_offsets(point)
        self.assertEqual([(-1, -1)], candidates)

    def test_get_highest_adjacent_points_as_directions_two(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point.translate(-1, -1), 99)
        self.tm.set_z(point.translate(0, -1), 99)
        candidates = self.tm.get_highest_adjacent_offsets(point)
        self.assertEqual([(-1, -1), (0, -1)], candidates)

    def test_get_highest_adjacent_points_as_directions_three(self):
        point = Point2D(10, 10)
        self.create_adjacent_data_at_point(point)
        self.tm.set_z(point.translate(-1, -1), 99)
        self.tm.set_z(point.translate(0, -1), 99)
        self.tm.set_z(point.translate(1, -1), 99)
        candidates = self.tm.get_highest_adjacent_offsets(point)
        self.assertEqual([(-1, -1), (0, -1), (1, -1)], candidates)

    def test_populate_from_matrix(self):
        self.tm = make_example_topology()
        height = len(TEST_MAP)
        width = len(TEST_MAP[0])
        for y in range(height):
            for x in range(width):
                row = height - y - 1  # row is reversed from y
                self.assertEqual(TEST_MAP[row][x], self.tm.get_z(Point2D(x, y)))

    def test_populate_from_matrix_origin_shift(self):
        self.tm = make_example_topology(origin=Point2D(10, 20))
        # The 4 is normally at point (6,4)
        self.assertEqual(4, self.tm.get_z(Point2D(16, 24)))

    def test_populate_from_matrix_without_setting_bounds(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20), set_bounds=False)
        self.assertNotEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(9, 22)))

    def test_before_min_bounds_x(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(9, 22)))

    def test_on_min_bounds_x(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertNotEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(10, 22)))

    def test_after_max_bounds_x(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(17, 22)))

    def test_on_max_bounds_x(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertNotEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(16, 22)))

    def test_before_min_bounds_y(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(12, 19)))

    def test_on_min_bounds_y(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertNotEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(12, 20)))

    def test_after_max_bounds_y(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(12, 26)))

    def test_on_max_bounds_y(self):
        """
        :return:
        """
        self.tm = make_example_topology(origin=Point2D(10, 20))
        self.assertNotEqual(OUT_OF_BOUNDS, self.tm.get_z(Point2D(12, 25)))
