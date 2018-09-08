class Topology(object):
    OUT_OF_BOUNDS = -1

    def __init__(self, topology_map):
        self.topology_map = topology_map
        self.width = len(topology_map[0]) # the width of the first row is the width of all rows
        self.height = len(topology_map)

    def get_height(self, point):
        """
        return height at a point. If height is off grid, return -1 since
        :param point:
        :return:
        """
        # Handle cases where the point lies off the topology
        if point.x < 0 or point.x >= self.width:
            return self.OUT_OF_BOUNDS
        if point.y < 0 or point.y >= self.height:
            return self.OUT_OF_BOUNDS

        return self.topology_map[point.y][point.x]
