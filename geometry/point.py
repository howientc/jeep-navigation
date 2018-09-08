class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def offset_x_y(self, offset):
        self.x += offset[0]
        self.y += offset[1]

    def __hash__(self):
        return hash(str(self.x) + '/' + str(self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return str(self.x) + ',' + str(self.y)
