import copy

from .navigation_strategy import NavigationStrategy


class MoveSensorWidthStrategy(NavigationStrategy):
    """
    This strategy will move just one space vertically, horizontally, or diagonally at a time
    """

    def navigate_to_extraction_point(self, start_point, move_callback=None):
        """
        :param start_point:
        :param move_callback: function called with 2 args: new_point and bearing for jeep to move
        :return:
        """
        pass

