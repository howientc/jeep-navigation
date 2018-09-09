from abc import ABC, abstractmethod
from .sensor_buffer import SensorBuffer


class TopologySensor(ABC):
    __slots__ = ['read_topology_count', 'cell_scan_count', '_buffer', 'topology_map']
    """
    Base class for topology sensors. They read the values of the terrain around them
    TODO Scan cost
    TODO Scan is per direction or total
    """

    def __init__(self, sensor_radius=1):
        """
        :param sensor_radius:
        """
        self._buffer = SensorBuffer(sensor_radius)
        self.read_topology_count = 0  # how many times sensor is fired up
        self.cell_scan_count = 0  # how many time scans of individual cells are done
        self.topology_map = None  # will be injected later by factory. can be passed in for testing

    def set_topology_map(self, topology_map):
        self.topology_map = topology_map

    def walk_points_with_known(self, point):
        for x, y, z, pt in self._buffer.walk_points(point):
            yield x, y, self.topology_map.get_z(pt), pt

    def _populate_adjacent_topology_from_known(self, field, point):
        # self.walk_scan(field)
        for x, y, z, pt in self.walk_points_with_known(point):
            field[y][x] = z

    def get_adjacent_topology(self, point):
        """
        :param point: current point of drone
        :return:
        """
        scanned = False
        for x, y, z, pt in self.walk_points_with_known(point):
            if z is None:
                z = self.scan(x, y, pt)
                self._buffer.set_z(x, y, z)
                self.topology_map.set_z(pt, z)
                self.cell_scan_count += 1
                scanned = True
        if scanned:
            self.read_topology_count += 1

        return self._buffer

    @abstractmethod
    def scan(self, x, y, point=None):
        """
        Request value at point
        :param x:
        :param y:
        :param point:
        :return:

        """
