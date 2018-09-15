# -*- coding: utf-8 -*-
"""
Simple immutable, hashable Point2D and Point3D classes
For purposes of this exercise, I am writing it myself, though in reality, the "Jeep" project
should use a geometry library, such as https://docs.sympy.org/latest/modules/geometry/index.html
Note that because of this, I'm keeping things simple and not bothering to write test cases. The code
is pretty trivial.
"""
import math


class Point2D(object):
    """
    immutable 2D point class
    """

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def translate2d(self, x, y):
        return Point2D(self._x + x, self._y + y)

    def translate(self, x, y):
        return self.translate2d(x, y)

    def distance2d(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def distance(self, other):
        return self.distance(other)

    def max_orthogonal_distance(self, other):
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def to_tuple(self):
        return self.x, self.y

    def midpoint_to(self, other):
        return Point2D((self.x + other.x) / 2, (self.y + other.y) / 2)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __hash__(self):
        return hash(str(self.x) + '/' + str(self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'


ORIGIN = Point2D(0, 0)


class Point3D(Point2D):
    """
    immutable 3D point class
    """

    def __init__(self, x, y, z):
        super().__init__(x, y)
        self._z = z

    @property
    def z(self):
        return self._z

    def translate3d(self, x, y, z):
        return Point3D(self._x + x, self._y + y, self._z + z)

    def distance(self, other):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def to_tuple(self):
        return self.x, self.y, self.z

    def to_2d(self):
        return Point2D(self.x, self.y)

    def __hash__(self):
        return hash(str(self.x) + '/' + str(self.y) + '/' + str(self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'
