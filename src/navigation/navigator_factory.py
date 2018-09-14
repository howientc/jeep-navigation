# -*- coding: utf-8 -*-
"""
Factory for making Navigators
"""
from navigation.move_strategy import MoveStrategyType, make_move_strategy
from navigation.navigator import Navigator


class NavigatorFactory(object):
    """
    Factory
    """

    @staticmethod
    def make_navigator(topology_map, move_strategy, destination):
        """
        Makes a navigator
        :param topology_map:
        :param move_strategy:
        :param destination:
        :return:
        """
        if isinstance(move_strategy, MoveStrategyType):
            move_strategy = make_move_strategy(move_strategy)

        return Navigator(topology_map=topology_map,
                         move_strategy=move_strategy,
                         destination=destination)
