from abc import ABC
from geometry.point2d import Point2D


class MoveStrategy(ABC):
    __slots__ = ['_number_of_cells_to_move', '_prefer_moving_to_lesser_known_points', '_prefer_cardinal_to_ordinal']

    def __init__(self, number_of_cells_to_move=1, prefer_moving_to_lesser_known_points=True,
                 prefer_cardinal_to_ordinal=True):
        self._number_of_cells_to_move = number_of_cells_to_move
        _prefer_moving_to_lesser_known_points = prefer_moving_to_lesser_known_points
        _prefer_cardinal_to_ordinal = prefer_cardinal_to_ordinal

    def move_n(self, point, direction):
        x, y = direction
        return point.offset(x * self._number_of_cells_to_move, y * self._number_of_cells_to_move)

    def move_1(self, point, direction):
        x, y = direction
        return point.offset(x, y)

    def choose_candidate_directions(self, directions):
        edges = edges_only(directions)
        corners = corners_only(directions)
        if self._prefer_cardinal_to_ordinal or not corners:
            return edges, True
        return corners, False

    def determine_new_point(self, topology_map, point, directions, cardinal_move_amount, ordinal_move_amount):
        candidate_directions, cardinal = self.choose_candidate_directions(directions)
        move_amount = cardinal_move_amount if cardinal else ordinal_move_amount
        # let's get the points that we'd move to
        move_points = offset_points_by_directions(point, candidate_directions, move_amount)

        # sort candidate points by how well we know the points around them
        sorted_move_points = sorted(move_points,
                                    key=lambda pt: topology_map.count_unknown_points_at_and_adjacent_to_point(pt))
        # pick least or most known point, based on our preference
        new_point = sorted_move_points[-1] if self.prefer_moving_to_lesser_known_points else sorted_move_points[0]
        return new_point


class NaiveMoveOneStrategy(MoveStrategy):
    """
    The Naive move 1 strategy. See README.md
    :param _topology_map: unused
    :param point:
    :param highest_directions:
    :return: a list containing one element, the point to move to
    """

    def __call__(self, _topology_map, point, directions):
        """
        :param _topology_map: unused
        :param point: current point we're at
        :param directions: list of directions to consider
        :return: a list containing one element, the point to move to
        """
        new_point = self.determine_new_point(topology_map, point, directions,
                                             cardinal_move_amount=1,
                                             ordinal_move_amount=1
                                             )
        return [new_point]


class MoveNCardinal1OrdinalStrategy(MoveStrategy):
    """
    A functor used to encapsulate the Move N cardinal, 1 ordinal variant
    See README.md for explanation
    """

    def __call__(self, _topology_map, point, highest_directions):
        """
        :param _topology_map: unused
        :param point: current point we're at
        :param highest_directions: list of high directions
        :return: a list containing one element, the point to move to
        """
        new_point = self.determine_new_point(topology_map, point, directions,
                                             cardinal_move_amount=self._number_of_cells_to_move,
                                             ordinal_move_amount=1
                                             )
        return [new_point]


class SmartOrdinalStrategy(MoveStrategy):
    def __call__(self, topology_map, point, directions):
        new_point = self.determine_new_point(topology_map, point, directions,
                                             cardinal_move_amount=self._number_of_cells_to_move
        ordinal_move == self._number_of_cells_to_move)
        # determine if this new point represents a cardinal move by seeing if x or y are unchanged
        cardinal = new_point.x == point.x or new_point.y == point.y
        if cardinal:
            return [new_point]

        # since we're moving to an ordinal (diagonal), need to prepare a path to move


def edges_only(directions):
    """
    Given a list of directions, choose the edges (not corners)
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x,y) for x,y in directions if x * y == 0]


def corners_only(directions):
    """
    Given a list of directions, choose the corners (not edges)
    :param directions: list of tuples (x,y)
    :return: list of tuples(x,y)
    """
    return [(x,y) for x,y in directions if x * y != 0]


def offset_points_by_directions(point, directions, amount):
    return [point.offest(amount * x, amount * y) for x, y in directions]
