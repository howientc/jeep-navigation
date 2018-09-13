from navigation.move_strategy import MoveStrategyType, make_move_strategy
from navigation.navigator import Navigator
from geometry.point import Point2D


class NavigatorFactory(object):

    @staticmethod
    def make_navigator(topology_map, move_strategy,
                       func_is_destination_point=None):
        if not func_is_destination_point:
            func_is_destination_point = NavigatorFactory.func_is_extraction_point()

        if isinstance(move_strategy, MoveStrategyType):
            move_strategy = make_move_strategy(move_strategy)

        return Navigator(topology_map=topology_map,
                         move_strategy=move_strategy,
                         func_is_destination_point=func_is_destination_point)

    @staticmethod
    def func_is_extraction_point():
        """
        For flexibility, this provides a means to specify a rule for determining if a point is an extraction point.
        This can be useful if the definition of extraction point can depend on something. For example, in bad
        weather, we might redefine an extraction point to one having a plateau of a size larger than 1. For now,
        just use standard definition, that an extraction point cell is higher (or equal to) its adjacent cells
        :return:
        """

        def highest_of_adjacent(topology_map, point):
            """
            Local method to hold a callback to the standard test test
            :param topology_map:
            :param point:
            :return:
            """
            return topology_map.is_highest_or_tie_in_radius(point)

        return highest_of_adjacent
