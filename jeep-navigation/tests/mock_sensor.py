import copy
from topology_sensor import TopologySensor

class MockSensor(TopologySensor):
    def __init__(self, mock_topology):
        super().__init__()
        self.mock_topology = mock_topology

    def get_adjacent_toplogy(self, point):
        cur_point = copy.copy(point) # mutable version to play with
        for y in range(3):
            for x in range(3):
                cur_point.offset_x_y((x - 1 , y - 1)) #subtracting one, because we want -1, 0, +1
                height = self.get_known_height(cur_point)
                if not height:
                    height = self.mock_topology.get_height(cur_point)
                    self.set_known_height(cur_point, height)
                self.adjacent_matrix[y][x] = height
        return self.adjacent_matrix