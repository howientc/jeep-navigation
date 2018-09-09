import unittest
from tests.topology.simulated_topology import SimulatedTopology
from geometry.point2d import Point2D

TEST_MAP = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 1, 1, 2, 4],
    [1, 2, 2, 2, 1, 2, 2],
    [1, 2, 3, 2, 1, 1, 1],
    [1, 1, 2, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 2],
]


class TestSimulatedTopology(unittest.TestCase):
    """
    Even though MockTopology is itself only used in testing, it should be tested itself,
    because if it's buggy, then other tests will fail because of it
    """
    def setUp(self):
        self.top = SimulatedTopology(TEST_MAP)

    def test_known(self):
        for y in range(self.top.height):
            for x in range(self.top.width):
                row = self.top.height - y - 1  # row is reversed from y
                self.assertEqual(TEST_MAP[row][x], self.top.get_z(Point2D(x, y)))

    def test_neg_x(self):
        """
        make sure we get -1 when off to left
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_z(Point2D(-1, 3)))

    def test_border_x(self):
        """
        make sure we get -1 when at right edge
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_z(Point2D(self.top.width, 3)))

    def test_border_y(self):
        """
        make sure we get -1 when at bottom edge
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_z(Point2D(1, self.top.height)))

    def test_big_x(self):
        """
        make sure we get -1 when way off to left
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_z(Point2D(99999, 3)))

    def test_big_y(self):
        """
        make sure we get -1 when way past bottom
        :return:
        """
        self.assertEqual(self.top.OUT_OF_BOUNDS, self.top.get_z(Point2D(1, 99999)))


if __name__ == '__main__':
    unittest.main()
