import unittest
from topology import Topology
from geometry.point import Point

TEST_MAP = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 1, 1, 2, 4],
    [1, 2, 2, 2, 1, 2, 2],
    [1, 2, 3, 2, 1, 1, 1],
    [1, 1, 2, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 2],
]


class TestTopology(unittest.TestCase):
    def setUp(self):
        self.top = Topology(TEST_MAP)

    def test_known(self):
        for y in range(self.top.height):
            for x in range(self.top.width):
                self.assertEqual(TEST_MAP[y][x], self.top.get_height(Point(x, y)))

    def test_negX(self):
        """
        make sure we get -1 when off to left
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_height(Point(-1, 3)))

    def test_border_x(self):
        """
        make sure we get -1 when at right edge
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_height(Point(self.top.width, 3)))

    def test_border_y(self):
        """
        make sure we get -1 when at bottom edge
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_height(Point(1, self.top.height)))

    def test_big_x(self):
        """
        make sure we get -1 when way off to left
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_height(Point(99999, 3)))

    def test_big_y(self):
        """
        make sure we get -1 when way past bottom
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_height(Point(1, 99999)))

if __name__ == '__main__':
    unittest.main()
