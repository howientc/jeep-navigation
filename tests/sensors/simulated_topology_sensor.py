from sensors.topology_sensor import TopologySensor


class SimulatedTopologySensor(TopologySensor):
    """
    A sensor used in testing. It serves to simulate reading values from MockTopology
    """
    __slots__ = ['_simulated_map']

    def __init__(self, simulated_map, topology_map=None):
        super().__init__()
        self._simulated_map = simulated_map
        self.set_topology_map(topology_map)

    def scan(self, unused_x, unused_y, point):
        """
        A real sensor wouldn't care about the point. It would just use x,y to scan the value
        at that offset from its center. Here, we need the point since we're getting the value
        from the mock topology and ignore the x and y args
        :param unused_x:
        :param unused_y:
        :param point: point where to get topology
        :return: z value at that point
        """
        return self._simulated_map.get_z(point)
