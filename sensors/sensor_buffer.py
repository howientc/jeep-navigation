from geometry.point2d import Point2D


class SensorBuffer(object):
    def __init__(self, radius):
        self._radius = radius
        self._size = radius + 2  # equal to twice the radius, but also the center value, so 1->3
        self.matrix = [[None for _x in range(self.size)] for _y in range(self.size)]

    @property
    def size(self):
        return self._size

    @property
    def radius(self):
        return self._radius

    def set_z(self, x, y, z):
        self.matrix[y][x] = z

    def walk_xyz(self):
        """
        Convenience method to iterate through all x,y values of the sensor buffer as a single generator,
        yielding x,y for each
        In other languages, a visitor pattern would be more appropriate (with a callback),
        but in Python, a generator is more appropriate due to the language's extensive support
        for generators, and also its lambdas are just inline or require more complex syntax
        :return:
        """
        for y in range(self.size):
            for x in range(self.size):
                yield x, y, self.matrix[y][x]

    def walk_points(self, point):
        """
        Convenience method to walk x,y and physical points
        :param point:
        :return:
        """
        for x, y, z in self.walk_xyz():
            pt = point.translate(x - self.radius, y - self.radius)
            yield x, y, z, pt

    # def is_center_biggest(self):
