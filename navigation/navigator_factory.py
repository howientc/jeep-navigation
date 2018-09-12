from navigation.move_strategy import MoveStrategyType, make_move_strategy
from navigation.navigator import Navigator


class NavigatorFactory(object):
    @staticmethod
    def make_navigator(topology_map, move_strategy,
                       func_is_destination_point):
        if isinstance(move_strategy, MoveStrategyType):
            move_strategy = make_move_strategy(move_strategy)

        return Navigator(topology_map=topology_map,
                         move_strategy=move_strategy,
                         func_is_destination_point=func_is_destination_point)
