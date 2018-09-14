import logging
from geometry.point import Point3D

try:
    from pydispatch import dispatcher  # see if PyDispatcher package exists
except ImportError:
    logging.warn("PyDistpatcher not found. Drone movement won't be published to observers")
    dispatcher = None


class Drone(object):
    __slots__ = ['_coords', '_topology_sensors', '_navigator']

    SIGNAL_MOVED = "Drone Moved"  # dispatches x,y,z of point
    SIGNAL_START = "Drone Started"  # dispatches x,y of start point
    SIGNAL_DESTINATION = "Drone Arrived"  # dispatches x,y,z of destination point

    def __init__(self, navigator, topology_sensors):
        """
        :param navigator:
        :param topology_sensors:
        """
        self._coords = Point3D(0, 0, 0)
        self._topology_sensors = topology_sensors
        self._navigator = navigator

    @property
    def navigator(self):
        return self._navigator

    def move_to(self, point):
        """
        Move the drone to the given 2d point.
        In the future, we could:
        - Use a Point3D in case we need to care about moving vertically because
        of increased power use due to overcoming gravity
        - Keep track of distance covered
        :param point: 2D point
        :return: path of points. last point is the destination
        """
        self._coords = point
        logging.info("Drone moved to " + repr(point))

    def navigate_to_extraction_point(self, start_point):
        logging.info("Start point is " + repr(start_point))
        self._coords = Point3D(start_point.x, start_point.y, 0)  # set start position without calling move_to
        # Notify any observers that the drone moved
        if dispatcher:
            dispatcher.send(signal=Drone.SIGNAL_START, pt=start_point, sender=self)

        point3d = None
        path = []
        for point3d in self._navigator.iter_points_to_destination(start_point=start_point,
                                                                  topology_sensors=self._topology_sensors):
            self.move_to(point3d)
            path.append(point3d)
            # Notify any observers that the drone moved
            if dispatcher:
                dispatcher.send(signal=Drone.SIGNAL_MOVED, pt=point3d, sender=self)

        if dispatcher:
            dispatcher.send(signal=Drone.SIGNAL_DESTINATION, pt=point3d, sender=self)
        return path
