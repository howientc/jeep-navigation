import sys

sys.path.extend(['.', './src', './tests', './examples'])

from geometry.point import Point2D, Point3D
from drone.drone_factory import DroneFactory
from navigation.move_strategy import MoveStrategyType
from sensors.simulated_topology_sensor import SimulatedTopologySensor

from ui.plot_topology_map import plot_topology_map
from tests.topology.topology_factory import TopologyFactory
import random


class PlotPathExample(object):
    def __init__(self):
        random.seed(100)  # for testing, we want to always genereate same map
        self.tm = TopologyFactory.make_fake_topology(upper_right=Point2D(20, 20))

        topology_sensors = [SimulatedTopologySensor(self.tm)]
        # move_strategy = MoveStrategyType.CLIMB_MOVE_1
        move_strategy = MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL
        # move_strategy = MoveStrategyType.SPIRAL_OUT_CW
        self.drone = DroneFactory.make_drone(move_strategy=move_strategy,
                                             topology_sensors=topology_sensors)

    def navigate(self, x, y):
        path = list(self.drone.navigate_to_extraction_point(Point2D(x, y)))
        found = self.drone.navigator.found
        # path.append(Point3D(found.x, found.y, 100))
        points = [pt.to_tuple() for pt in path]  # convert from Point3D list to tuple list
        print("Found destination at", found)
        print("last point is", points[-1])
        print(*points)
        return points

    def run(self):
        plot_topology_map(self.tm, lambda x, y: self.navigate(x, y))  # unittest will catch any exception


if __name__ == '__main__':
    example = PlotPathExample()
    example.run()
