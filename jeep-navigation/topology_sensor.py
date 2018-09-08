from abc import ABC, abstractmethod


class TopologySensor(ABC):
    def __init__(self):
        self.known_heights = defaultdict()  # keeps track of points already tracked to reduce cost of firing laser
        self.adjacent_matrix = [[0 for x in range(3)] for y in range(3)]

    def get_known_height(self, point):
        return self.known_heights.get(point)

    def set_known_height(self, point, height):
        self.known_heights[point] =  height

    @abstractmethod
    def get_adjacent_toplogy(self, point):
        """
        Sensors must fill this in
        :param point:
        :return:
        """