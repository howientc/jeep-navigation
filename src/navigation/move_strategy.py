# -*- coding: utf-8 -*-
"""
Move strategies are Functors (or simple functions) which given a point,  map, and destination type, will determine
where to go next. Move strategies are the brains for the Navigator. You can imagine that we would apply different
strategies in different situations. For example, if we're searching for high ground (extraction point), we'd be
likely to use a strategy that is always moving to higher ground. If we're doing a search/rescue, we might want
to spiral out from the start point to make sure we cover every square. A Navigator is free to change strategies
at any time. It could be programmed to first do a search/rescue, and then move to high ground.
"""
import math
from enum import Enum
from geometry.point import Point2D


class MoveStrategyType(Enum):
    """
    Enumeration of predefined strategies. This list should grow. For example, we could have variants
    for preferring ordinal over cardinal movements.
    """
    CLIMB_MOVE_1 = 0
    CLIMB_3_CARDINAL_1_ORDINAL = 1
    SPIRAL_OUT_CW_3 = 2
    SPIRAL_OUT_CCW = 3
    BINARY_SEARCH = 4


# For SpiralOutStrategy
CCW = [(0, 1), (-1, 0), (0, -1), (1, 0)]  # Counter-clockwise rotation
CW = CCW[::-1]  # Clockwise rotation

BINARY_SEARCH_MOVE_AMOUNT = 6


def make_move_strategy(s):
    """
    Makes a strategy from a strategy type. In the future, maybe create another factory method
    with more flexible input
    :param s: MoveStrategyType
    :return: A functor (or function)
    """
    if s == MoveStrategyType.CLIMB_MOVE_1:
        return ClimbStrategy("Climb Move 1", cardinal_move_amount=1, ordinal_move_amount=1)
    elif s == MoveStrategyType.CLIMB_3_CARDINAL_1_ORDINAL:
        return ClimbStrategy("Climb Move 3 card, 1 ord1", cardinal_move_amount=3, ordinal_move_amount=1)
    elif s == MoveStrategyType.BINARY_SEARCH:
        return BinarySearchStrategy("Binary Search", cardinal_move_amount=BINARY_SEARCH_MOVE_AMOUNT,
                                    ordinal_move_amount=BINARY_SEARCH_MOVE_AMOUNT,
                                    cardinal_range=range(BINARY_SEARCH_MOVE_AMOUNT, 3, -1),
                                    ordinal_range=range(BINARY_SEARCH_MOVE_AMOUNT, 1, -1)
                                    )
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
                 prefer_cardinal_to_ordinal=True):
        self.name = name
        self._cardinal_move_amount = cardinal_move_amount
        self._ordinal_move_amount = ordinal_move_amount
        self._prefer_moving_to_lesser_known_points = prefer_moving_to_lesser_known_points
        self._prefer_cardinal_to_ordinal = prefer_cardinal_to_ordinal

    def __call__(self, topology_map, point, destination):
        """
        Gets next point: Functor function: i.e. my_move_strategy(topology_map, point, directions)
        :param topology_map: our map
        :param point: current point we're at
        :param destination: Destination object
        :return: next Point to move to
        """

        # climb strategy wants to move up, so lets find highest points
        radius = destination.radius_needed_to_check
        directions = [(x, y) for x, y, _z, _pt in topology_map.list_highest_x_y_z_pt_in_radius(point, radius)]

        new_point, cardinal = self._determine_new_point(topology_map, point, directions, radius)
        return new_point

    def _choose_candidate_directions(self, directions):
        """
        Picks cardinal or ordinal directions depending on preferences and if there are any
        :param directions: list of (x,y) values of the offsets around the point
        :return:
        """
        edges = edges_only(directions)
        corners = corners_only(directions)
        if edges and (self._prefer_cardinal_to_ordinal or not corners):
            return edges, True
        return corners, False

    def _determine_new_point(self, topology_map, point, directions, radius):
        """
        Determines where to go next
        :param topology_map:
        :param point:
        :param directions:
        :param radius:
        :return:
        """
        candidate_directions, cardinal = self._choose_candidate_directions(directions)
        move_amount = self._cardinal_move_amount if cardinal else self._ordinal_move_amount
        # let's get the points that we'd move to
        move_points = translate_points_by_directions(point, candidate_directions, move_amount)

        # sort candidate points by how well we know the points around them
        sorted_move_points = sorted(move_points,
                                    key=lambda pt: topology_map.count_unknown_in_radius(pt, radius))

        # pick least or most known point, based on our preference
        if not sorted_move_points:
            new_point = point  # just in case this ever happens, pick same point and fix below
        else:
            new_point = sorted_move_points[-1] if self._prefer_moving_to_lesser_known_points else sorted_move_points[0]

        # Handle special case of moving back to a known point. For now, pick a simple rule to move perpendicularly
        # one square, either up or down. This can be improved, but it's not so common so optimize later
        while topology_map.count_unknown_in_radius(new_point, radius) == 0:  # if next point is already visited
            perp = ((point.y - new_point.y) // move_amount, (point.x - new_point.x) // move_amount)
            new_point = new_point.translate(*perp)
        return new_point, cardinal


class BinarySearchStrategy(ClimbStrategy):
    """
    A strategy that starts off with big steps. If it detects it went the wrong way, it moves halfway back
    to the known highest point. Otherwise, it uses the default base class movement. With each step, it reduces
    how much it moves by one. This strategy is good for maps with very few destnation points. It can be tuned
    according to the bumpiness of the terrain. Smoother terrain should have large initial steps
    """
    __slots__ = ['highest_point', 'amount_range', 'cardinal_range', 'ordinal_range']

    def __init__(self, *args, **kwargs):
        self.cardinal_range = kwargs.pop('cardinal_range')  # range of move_amounts
        self.ordinal_range = kwargs.pop('ordinal_range')  # range of move_amounts
        super().__init__(*args, **kwargs)
        self.highest_point = None

    def _decrement(self):
        """
        Decreases our move amounts. For now, just subtract 1 and stay in range
        """
        if self._cardinal_move_amount in self.cardinal_range:
            self._cardinal_move_amount -= 1
        if self._ordinal_move_amount in self.ordinal_range:
            self._ordinal_move_amount -= 1

    def __call__(self, topology_map, point, destination):
        """
        Determne next point by bisecting towards it in decreasing increments
        :param topology_map:
        :param point:
        :param destination:
        :return:
        """
        next_point = super().__call__(topology_map, point, destination)
        self._decrement()

        if self.highest_point:
            # see if if we moved downhill last time
            if topology_map.get_z(self.highest_point) > topology_map.get_z(point):
                # we went downhill, so bisect back to high point
                midpoint = point.midpoint_to(self.highest_point)
                return Point2D(math.floor(midpoint.x), math.floor(midpoint.y))
            else:
                self.highest_point = point  # this point is new high
        else:
            self.highest_point = point  # initialize now that we have a point
        return next_point


class SpiralOutStrategy(object):
    """
    A strategy that spirals out from a center point blindly.
    Note that for simulated maps that have bounds, it go out of bounds if it needs to
    """

    def __init__(self, name, rotation, step=1):
        self.name = name
        self._rotation = list(rotation)  # get rotation as point list
        self._step = step
        self._gen = self._iter_offset()

    def _iter_offset(self):
        """
        Generates next offset values to use
        :return:
        """
        index = 0
        length = 1
        while True:
            for _ in range(2):
                for _l in range(length):
                    yield [self._step * k for k in self._rotation[index]]
                index = (index + 1) % len(self._rotation)
            length += 1

    def __call__(self, topology_map, point, destination):
        """
        Gets next point (functor)
        :param topology_map:
        :param point:
        :param destination:
        :return: Next point
        """
        offset = next(self._gen)  # get next point from generator
        return point.translate(*offset)


def edges_only(directions):
    """
    Chooses edge points in directions directions
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x, y) for x, y in directions if x * y == 0]


def corners_only(directions):
    """
    Chooses corner points in directions
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x, y) for x, y in directions if x * y != 0]


def translate_points_by_directions(point, directions, amount):
    """
    Translates all points by a distance
    :param point:
    :param directions: list of (x,y) offsets
    :param amount: A factor used to increase the distance
    :return: list of new point values
    """
    return [point.translate(amount * x, amount * y) for x, y in directions]
