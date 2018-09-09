class Point2D(object):
    """
    immutable point class
    For purposes of this exercise, I am writing it myself, though in reality, the "Jeep" project
    should use a geometry library, such as https://docs.sympy.org/latest/modules/geometry/index.html
    Note that because of this, I'm keeping it small and not bothering to write test cases
    """
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def translate(self, x, y):
        return Point2D(self._x + x, self._y + y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __hash__(self):
        return hash(str(self.x) + '/' + str(self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'
