from enum import Enum, auto
from geometry.point import Point2D


class MoveStrategyType(Enum):
    NAIVE_MOVE_ONE = auto()
    MOVE_3_CARDINAL_1_ORDINAL = auto()
    SMART_ORIDINAL = auto()
    MOVE_N_CARDINAL_M_ORDINAL = auto()


def make_move_strategy(s):
    if s == MoveStrategyType.NAIVE_MOVE_ONE:
        return MoveStrategy(cardinal_move_amount=1, ordinal_move_amount=1)
    elif s == MoveStrategyType.MOVE_3_CARDINAL_1_ORDINAL:
        return MoveStrategy(cardinal_move_amount=3, ordinal_move_amount=1)
    elif s == MoveStrategyType.SMART_ORIDINAL:
        return SmartOrdinalStrategy(cardinal_move_amount=3, ordinal_move_amount=3)
    else:
        raise KeyError('Unknown strategy type')


class MoveStrategy(object):
    """
    A move strategy is just a function which receives (topology_map, point, directions).
    If a strategy requires keeping track of its state, then it needs to be an object. To get objects
    to behave like functions, we must use functors. To make a functor, define the __call__ method in
    the class.
    """
    __slots__ = ['_cardinal_move_amount', '_ordinal_move_amount', '_prefer_moving_to_lesser_known_points',
                 '_prefer_cardinal_to_ordinal']

    def __init__(self, cardinal_move_amount=1, ordinal_move_amount=1, prefer_moving_to_lesser_known_points=True,
                 prefer_cardinal_to_ordinal=True):
        self._cardinal_move_amount = cardinal_move_amount
        self._ordinal_move_amount = ordinal_move_amount
        self._prefer_moving_to_lesser_known_points = prefer_moving_to_lesser_known_points
        self._prefer_cardinal_to_ordinal = prefer_cardinal_to_ordinal

    def __call__(self, topology_map, point, directions):
        """
        Functor function: i.e. my_move_strategy(topology_map, point, directions)
        :param topology_map: unused
        :param point: current point we're at
        :param directions: list of directions to consider
        :return: a list containing one element, the point to move to
        """
        new_point = self._determine_new_point(topology_map, point, directions)
        return [new_point]

    def _choose_candidate_directions(self, directions):
        """
        Picks cardinal or ordinal directions depending on preferences and if there are any
        :param directions:
        :return:
        """
        edges = edges_only(directions)
        corners = corners_only(directions)
        if self._prefer_cardinal_to_ordinal or not corners:
            return edges, True
        return corners, False

    def _determine_new_point(self, topology_map, point, directions):
        candidate_directions, cardinal = self._choose_candidate_directions(directions)
        move_amount = self._cardinal_move_amount if cardinal else self._ordinal_move_amount
        # let's get the points that we'd move to
        move_points = translate_points_by_directions(point, candidate_directions, move_amount)

        # sort candidate points by how well we know the points around them
        sorted_move_points = sorted(move_points,
                                    key=lambda pt: topology_map.count_unknown_points_at_and_adjacent_to_point(pt))
        # pick least or most known point, based on our preference
        new_point = sorted_move_points[-1] if self._prefer_moving_to_lesser_known_points else sorted_move_points[0]
        return new_point, cardinal


class SmartOrdinalStrategy(MoveStrategy):
    def __call__(self, topology_map, point, directions):
        new_point, cardinal = self._determine_new_point(topology_map, point, directions)
        if cardinal:  # if moving cardinally, then we'll just return the point
            return [new_point]

        # For now just go right, up, then left. We could, in theory, check if we've already scanned at the points
        # and not bother moving there
        path = [Point2D(new_point.x, point.y), new_point, Point2D(point.x, new_point.y)]
        return path  # TODO consider optimizing the path by removing a point if it's already been seen


def edges_only(directions):
    """
    Given a list of directions, choose the edges (not corners)
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x, y) for x, y in directions if x * y == 0]


def corners_only(directions):
    """
    Given a list of directions, choose the corners (not edges)
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x, y) for x, y in directions if x * y != 0]


def translate_points_by_directions(point, directions, amount):
    return [point.translate(amount * x, amount * y) for x, y in directions]
