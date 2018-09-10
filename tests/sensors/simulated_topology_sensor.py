from sensors.topology_sensor import TopologySensor


class SimulatedTopologySensor(TopologySensor):
    """
    A sensor used in testing. It serves to simulate reading values from MockTopology
    """

    __slots__ = ['_simulated_map']

    def __init__(self, simulated_map, radius=1, power_on_cost=0, scan_point_cost=0):
        super().__init__(radius, power_on_cost, scan_point_cost)
        self._simulated_map = simulated_map

    def scan_points(self, offsets, home_point):
        """
        A real sensor would only care about the home_point to pass it back in the returned list. Here, though,
        we use it to lookup into the simulated topology
        :param offsets: A list of (x,y) tuples to scan
        :param home_point: the physical point at 0,0
        :return: a list of of tuples (x,y,z, point) corresponding to the values of points that were read.
        """
        scanned_points = []
        for x,y in offsets:
            point = home_point.translate(x,y)
            z = self._simulated_map.get_z(point)
            scanned_points.add(x, y, z, point)

        self._scan_point_count += 1
        scan_cost = self.scan_point_cost * len(scanned_points)  # maybe we want to return this also?
        self._total_cost += scan_cost
        return scanned_points
