from topology.topology_map import TopologyMap
from geometry.point2d import Point2D


class SimulatedTopology(TopologyMap):
    """
    Subclass of TopologyMap that lets us build a map from a matrix. This
    map can then be used by the SimulatedTopologySensor to get values
    """

    # We can think of any point not part of our map as OUT_OF_BOUNDS. Conceptually, it's like
    # saying that we're on an island and OUT_OF_BOUNDS is water, which is below any adjacent land
    # I picked the smallest possible value for the constant, so we  could support negative heights in the future
    OUT_OF_BOUNDS = float("-inf")

    def __init__(self, topology_matrix):
        """
        We construct a topology map from a matrix, treating it as if the matrix's lower left
        corner sits on point(0,0) on the cartesian plane. X values correspond directly
        to the matrix column, but the rows need to be reversed
        :param topology_matrix:
        """

        super().__init__()
        self.width = len(topology_matrix[0])  # the width of the first row is the width of all rows
        self.height = len(topology_matrix)
        for row in range(self.height):
            for col in range(self.width):
                # reversing rows to make y value
                self.set_z(Point2D(col, self.height - row - 1), topology_matrix[row][col])

    def get_z(self, point):
        """
        return z ( the height) at a point. If point is off grid, return OUT_OF_BOUNDS.
        :param point:
        :return:
        """
        # Handle cases where the point lies off the topology
        if point.x < 0 or point.x >= self.width:
            return self.OUT_OF_BOUNDS
        if point.y < 0 or point.y >= self.height:
            return self.OUT_OF_BOUNDS

        return super(SimulatedTopology, self).get_z(point)  # we're in bounds, so can look in cache
