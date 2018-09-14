from enum import Enum, auto


class MoveStrategyType(Enum):
    CLIMB_MOVE_1 = 0
    CLIMB_3_CARDINAL_1_ORDINAL = 1
    SPIRAL_OUT_CW_3 = 2
    SPIRAL_OUT_CCW = 3
    FIND_RIDGELINE_THEN_CLIMB_3_CARDINAL_1_ORDINAL = 4


# For SpiralOutStrategy
CCW = [(0, 1), (-1, 0), (0, -1), (1, 0)]  # Counter-clockwise rotation
CW = CCW[::-1]  # Clockwise rotation

BINARY_SEARCH_MOVE_AMOUNT = 10


def make_move_strategy(s):
    if s == MoveStrategyType.CLIMB_MOVE_1:
        return ClimbStrategy("Climb Move 1", cardinal_move_amount=1, ordinal_move_amount=1)
    elif s == MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL:
        return ClimbStrategy("Climb Move 3 card, 1 ord1", cardinal_move_amount=3, ordinal_move_amount=1)
    elif s == MoveStrategyType.FIND_RIDGELINE_THEN_CLIMB_3_CARDINAL_1_ORDINAL:
        return RidgelineStrategy("Ridgline", move_amount=BINARY_SEARCH_MOVE_AMOUNT,
                                 switch_to=MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL)
    elif s == MoveStrategyType.SPIRAL_OUT_CW_3:
        return SpiralOutStrategy("Spiral Clockwise 3", CW, 3)
    elif s == MoveStrategyType.SPIRAL_OUT_CCW:
        return SpiralOutStrategy("Spiral Counter-Clockwise", CCW)
    else:
        raise KeyError('Unknown strategy type')


class ClimbStrategy(object):
    """
    A climb strategy is just a function which receives (topology_map, point, directions).
    If a strategy requires keeping track of its state, then it needs to be an object. To get objects
    to behave like functions, we must use functors. To make a functor, define the __call__ method in
    the class.
    """
    __slots__ = ['name', '_cardinal_move_amount', '_ordinal_move_amount', '_prefer_moving_to_lesser_known_points',
                 '_prefer_cardinal_to_ordinal']

    def __init__(self, name, cardinal_move_amount=1, ordinal_move_amount=1, prefer_moving_to_lesser_known_points=True,
                 prefer_cardinal_to_ordinal=False):
        self.name = name
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
        if not sorted_move_points:
            print(*directions)
            print(*candidate_directions)
            print(*move_points)
            assert False
        new_point = sorted_move_points[-1] if self._prefer_moving_to_lesser_known_points else sorted_move_points[0]
        return new_point, cardinal


class RidgelineStrategy(object):
    __slots__ = ['_switch_to', '_switch_to_strategy', '_move_amount']

    def __init__(self, name, move_amount, switch_to):
        self.name = name
        self._move_amount = move_amount
        self._switch_to = switch_to
        self._switch_to_strategy = None

    def __call__(self, topology_map, point, directions):
        if self._switch_to_strategy:
            return self._switch_to_strategy(topology_map, point, directions)

        # TODO implement binary search and switch when ridge found
        raise Exception("RidgelineStrategy is not implemented yet")


class SpiralOutStrategy(object):
    """
    A strategy that spirals out from a center point blindly.
    Note that for simulated maps that have bounds, it go out of bounds if it needs to
    """

    def __init__(self, name, rotation=CW, step=1):
        self.name = name
        self._rotation = list(rotation)  # get rotation as point list
        self._step = step
        self._gen = self._iter_offset()

    def _iter_offset(self):
        index = 0
        length = 1
        while True:
            for _ in range(2):
                for _l in range(length):
                    yield [self._step * k for k in self._rotation[index]]
                index = (index + 1) % len(self._rotation)
            length += 1

    def __call__(self, topology_map, point, destination):
        offset = next(self._gen)  # get next point from generator
        return point.translate(*offset)


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
