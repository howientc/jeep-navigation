# -*- coding: utf-8 -*-
"""
Functors which serve to return whether a point on a map is a destination (e.g. extraction point). The functors
also have a radius_needed_to_check property which gives the radius of points that need to be scanned for the
functor's function (__call__) to be able to be evaluated
"""

from abc import ABC, abstractmethod


class Destination(ABC):
    """
    Base class for Functors which determine if a point is a destination
    """
    @property
    @abstractmethod
    def radius_needed_to_check(self):
        """
        radius of cells needed to verify if we're on a destination. If the point itself is sufficient, then
        radius is 0. If immediately surrounding cells are needed, then radius is 1
        :return:
        """


class ExtractionPoint(Destination):
    """
    Determines if a point is an extraction point by seeing if it's the highest in its surroundings.
    This is a functor method
    """
    def __call__(self, topology_map, point):
        return topology_map.is_highest_or_tie_in_radius_and_all_known(point, self.radius_needed_to_check)

    @property
    def radius_needed_to_check(self):
        """
        Gets radius. Extraction point test checks 1 point on all sides of a given point, so radius =1
        :return:
        """
        return 1
