import copy

from .navigation_strategies import NavigationStrategy


class MoveOneStrategy(NavigationStrategy):
    """
    This strategy will move just one space vertically, horizontally, or diagonally at a time
    """
    # def __init__(self, topology_sensor):
    #     super.__init__(topology_sensor)

    def navigate_to_extraction_point(self, start_point, move_callback=None):
        """
        :param start_point:
        :param move_callback: function called with 2 args: new_point and bearing for jeep to move
        :return:
        """
        point = copy.copy(start_point)  # don't mutate the input in case it's used elsewhere
        while True:
            bearing = self._get_bearing_to_higher_ground(point)
            if bearing == (0, 0):
                return point
            point.translate(bearing)
            if move_callback:
                move_callback(point, bearing)  # move to this point in this direction

