from enum import Enum, auto


class MoveStrategyType(Enum):
    CLIMB_MOVE_1 = auto()
    CLIMB_3_CARDINAL_1_ORDINAL = auto()
    FIND_RIDGELINE_THEN_CLIMB_3_CARDINAL_1_ORDINAL = auto()
    SPIRAL_OUT_CW = auto()
    SPIRAL_OUT_CCW = auto()


# For SpiralOutStrategy
CCW = ((0, 1), (-1, 0), (0, -1), (1, 0))  # Counter-clockwise rotation
CW = ((0, 1), (1, 0), (0, -1), (-1, 0))  # Clockwise rotation
BINARY_SEARCH_MOVE_AMOUNT = 10


def make_move_strategy(s):
    if s == MoveStrategyType.CLIMB_MOVE_1:
        return ClimbStrategy(cardinal_move_amount=1, ordinal_move_amount=1)
    elif s == MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL:
        return ClimbStrategy(cardinal_move_amount=3, ordinal_move_amount=1)
    elif s == MoveStrategyType.FIND_RIDGELINE_THEN_CLIMB_3_CARDINAL_1_ORDINAL:
        return RidgelineStrategy(move_amount=BINARY_SEARCH_MOVE_AMOUNT,
                                 switch_to=MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL)
    elif s == MoveStrategyType.SPIRAL_OUT_CW:
        return SpiralOutStrategy(CW)
    elif s == MoveStrategyType.SPIRAL_OUT_CCW:
        return SpiralOutStrategy(CCW)
    else:
        raise KeyError('Unknown strategy type')


class ClimbStrategy(object):
    """
    A climb strategy is just a function which receives (topology_map, point, directions).
    If a strategy requires keeping track of its state, then it needs to be an object. To get objects
    to behave like functions, we must use functors. To make a functor, define the __call__ method in
    the class.
    """
    __slots__ = ['_cardinal_move_amount', '_ordinal_move_amount', '_prefer_moving_to_lesser_known_points',
                 '_prefer_cardinal_to_ordinal']

    def __init__(self, cardinal_move_amount=1, ordinal_move_amount=1, prefer_moving_to_lesser_known_points=True,
                 prefer_cardinal_to_ordinal=False):
        self._cardinal_move_amount = cardinal_move_amount
        self._ordinal_move_amount = ordinal_move_amount
        self._prefer_moving_to_lesser_known_points = prefer_moving_to_lesser_known_points
        self._prefer_cardinal_to_ordinal = prefer_cardinal_to_ordinal

    def __call__(self, topology_map, point, destination):
        """
        Functor function: i.e. my_move_strategy(topology_map, point, directions)
        :param topology_map: unused
        :param point: current point we're at
        :param destination: Destination object
        :return: a list containing one element, the point to move to
        """

        # climb strategy wants to move up, so lets find highest points
        radius = destination.radius_needed_to_check
        directions = [(x, y) for x, y, _z, _pt in topology_map.list_highest_x_y_z_pt_in_radius(point, radius)]

        new_point, cardinal = self._determine_new_point(topology_map, point, directions, radius)
        return new_point

    def _choose_candidate_directions(self, directions):
        """
        Picks cardinal or ordinal directions depending on preferences and if there are any
        :param directions:
        :return:
        """
        edges = edges_only(directions)
        corners = corners_only(directions)
        if edges and (self._prefer_cardinal_to_ordinal or not corners):
            return edges, True
        return corners, False

    def _determine_new_point(self, topology_map, point, directions, radius):
        candidate_directions, cardinal = self._choose_candidate_directions(directions)
        move_amount = self._cardinal_move_amount if cardinal else self._ordinal_move_amount
        # let's get the points that we'd move to
        move_points = translate_points_by_directions(point, candidate_directions, move_amount)

        # sort candidate points by how well we know the points around them
        sorted_move_points = sorted(move_points,
                                    key=lambda pt: topology_map.count_unknown_in_radius(pt, radius))
        # pick least or most known point, based on our preference
        new_point = sorted_move_points[-1] if self._prefer_moving_to_lesser_known_points else sorted_move_points[0]
        return new_point, cardinal


class RidgelineStrategy(object):
    __slots__ = ['_switch_to', '_switch_to_strategy', '_move_amount']

    def __init__(self, move_amount, switch_to):
        self._move_amount = move_amount
        self._switch_to = switch_to
        self._switch_to_strategy = None

    def __call__(self, topology_map, point, directions):
        if self._switch_to_strategy:
            return self._switch_to_strategy(topology_map, point, directions)

        # TODO implement binary search and switch when ridge found
        raise Exception("RidgelineStrategy is not implemented yet")


class SpiralOutStrategy(object):
    def __init__(self, rotation=CW, step=1):
        self._counter = 0
        self._rotation = list(rotation)  # get rotation as point list
        self._step = step

    def __call__(self, topology_map, point, directions):
        move_amount = self._step * (1 + self._counter // 2)
        direction = self._rotation[self._counter % len(self._rotation)]
        new_point = point.translate(direction[0] * move_amount, direction[1] * move_amount)
        return new_point, True


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
