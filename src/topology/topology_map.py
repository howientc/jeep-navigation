# -*- coding: utf-8 -*-
"""
A TopologyMap is essentially like a real topology map. Think of it as a piece of graph paper, in which every known
cell has a height value. The Navigator draws values in the cells as it uses scanners.
"""
from geometry.point import Point2D, Point3D

OUT_OF_BOUNDS = float("-inf")
NO_BOUNDS = float("inf")


class TopologyMap(object):
    """
    The map keeps track of all of the areas where it's
    already been. This helps us avoid rescanning areas that we've already scanned. Currently this
    map is regenerated every run. In the future, we can persist and then it can
    be used by any drone on a mission to the area. We could also persist the extraction points that
    have been discovered.

    This class contains many small helper methods for querying and generating points in a radius around a given point.
    """

    __slots__ = ['_known_z', '_lower_left', '_upper_right', '_lower_left_bounds', '_upper_right_bounds']

    def __init__(self, lower_left_bounds=None, upper_right_bounds=None):
        self._known_z = dict()  # keeps track of points already tracked to reduce cost of firing laser

        self._lower_left_bounds = lower_left_bounds
        self._upper_right_bounds = upper_right_bounds

        # for convenience, let's store off a list of offsets from 0, 0 to use in adjacent calculations
        self._lower_left = None
        self._upper_right = None

    def point_is_out_of_bounds(self, point):
        """
        Sees if point lies within valid bounds. Mostly needed for test topologies
        :param point:
        :return:
        """
        if self._lower_left_bounds and (point.x < self._lower_left_bounds.x or point.y < self._lower_left_bounds.y):
            return True

        if self._upper_right_bounds and (point.x > self._upper_right_bounds.x or point.y > self._upper_right_bounds.y):
            return True

        return False

    def get_z(self, point, default=None):
        """
        Gets z value (height) at a point. If out of bounds, returns OUT_OF_BOUNDS
        :param point:
        :param default:
        :return:
        """
        if self.point_is_out_of_bounds(point):
            return OUT_OF_BOUNDS

        found = self._known_z.get(point)
        return found if found else default

    def set_z(self, point, height):
        """
        Sets z value at a point to the passed height
        :param point:
        :param height:
        """
        self._known_z[point] = height

        # adjust our current bounds
        if not self._upper_right:
            self._upper_right = self._lower_left = point
        else:
            self._upper_right = Point2D(max(self._upper_right.x, point.x), max(self._upper_right.y, point.y))
            self._lower_left = Point2D(min(self._lower_left.x, point.x), min(self._lower_left.y, point.y))

    def make_3d(self, point2d):
        """
        Converts a 2d point to a 3d one by looking up its z value
        :param point2d:
        :return: Point3D
        """
        return Point3D(point2d.x, point2d.y, self.get_z(point2d))

    @property
    def width_and_height(self):
        """
        Gets the width and height of the rectangular bounds containing all known points. Since a point takes up
        one square unit of space, make sure to add 1 to the both dimensions
        :return:
        """
        return 1 + self._upper_right.x - self._lower_left.x, 1 + self._upper_right.y - self._lower_left.y

    @property
    def boundary_points(self):
        """
        Gets the lower left and upper right points of the rectangular bounds containing all known points
        :return: tuplo(lower left corner, upper right corner)
        """
        return self._lower_left, self._upper_right

    def iter_all_points_xyz(self):
        """
        Generates all of the known points in the map as x,y,z in no specific order
        :return: generator yielding x,y,z
        """
        return ((pt.x, pt.y, z) for pt, z in self._known_z.items())

    def iter_x_y_z_pt_in_radius(self, point, radius):
        """
        Generates all points in radius, known or not
        :param radius:
        :param point: center point
        :return: generator yielding x, y, z, pt
        """
        point.translate(0, 2)
        for (x, y) in iter_x_y_in_radius(radius):
            pt = point.translate(x, y)
            z = self._known_z.get(pt)
            yield x, y, z, pt

    def count_unknown_in_radius(self, point, radius):
        """
        Calculates how many points we've not seen yet in a radius out from this point
        :param point:
        :param radius:
        :return: number of points unknown
        """
        return len(self.list_unknown_x_y_in_radius(point, radius))

    def list_unknown_x_y_in_radius(self, point, radius):
        """
        :param point:
        :param radius:
        :return: list of unknown points
        """
        return [(x, y) for x, y, _pt in self.iter_unknown_x_y_pt_in_radius(point, radius)]

    def iter_unknown_x_y_pt_in_radius(self, point, radius):
        """
        Generates x,y,pt to all unknown cells within a radius of point.
        :param point:
        :param radius:
        :return: generator of x,y,z point
        """
        return ((x, y, pt) for x, y, known, pt in self.iter_x_y_z_pt_in_radius(point, radius) if not known)

    def iter_known_x_y_z_pt_in_radius(self, point, radius):
        """
        Generates x,y,z,pt for unknown cells within a radius of point.
        :param point:
        :param radius:
        :return: Generator x,y,z,pt
        """
        return ((x, y, z, pt) for x, y, z, pt in self.iter_x_y_z_pt_in_radius(point, radius) if z)

    def list_highest_x_y_z_pt_in_radius(self, point, radius):
        """
        Gets a list of the point or points in the radius having the maximal height value in the area within the radius
        :param point:
        :param radius:
        :return: list of highest points
        """
        # Figure out the max height by walking adjacent points and maxing on the z value
        known = list(self.iter_known_x_y_z_pt_in_radius(point, radius))
        if not known:
            print("not known at", point)
            return []

        max_z = max(z for (_x, _y, z, _pt) in known)

        # Now get the highest adjacent offsets as (x,y) tuples
        return [(x, y, z, pt) for (x, y, z, pt) in known if z == max_z]

    def is_highest_or_tie_in_radius_and_all_known(self, point, radius):
        """
        Sees if the point is equal or higher than all points adjacent to it on the condition
        that all of the adjacent points have already been scanned
        :param radius:
        :param point:
        :return: True if the point is highest (or tied), False if not, or not all of the adjacent
        points are known
        """
        if self.count_unknown_in_radius(point, radius):
            return False
        for _x, _y, z, pt in self.list_highest_x_y_z_pt_in_radius(point, radius):
            if pt == point:
                return True
        return False


def iter_x_y_in_radius(radius):
    """
    Generates all cells in a given radius
    :param radius:
    :return: yields x,y offsets from the center
    """
    size = range(-radius, radius + 1)
    return ((x, y) for y in size for x in size)

