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
        return topology_map.is_highest_or_tie_in_radius(point, self.radius_needed_to_check)

    @property
    def radius_needed_to_check(self):
        return 1  # need 1 point in all directions around the given point
