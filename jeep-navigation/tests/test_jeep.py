import unittest

class TestNavigation(unittest.TestCase):
    def setUp(self):
        topology = Topology(TEST_MAP)
        sensor = MockLaserSensor(topology)
        self.jeep = Jeep(sensor)

    def xtest_example(self):
        self.assertTrue(self.jeep.navigate_to_extraction_point(Point(2, 1)), Point(6, 1))

if __name__ == '__main__':
    unittest.main()
