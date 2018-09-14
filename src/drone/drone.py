# -*- coding: utf-8 -*-
"""
Drone Class. Could be used as base class for any vehicle
"""
import logging
from geometry.point import Point3D

try:
    from pydispatch import dispatcher  # see if PyDispatcher package exists
except ImportError:
    logging.warn("PyDistpatcher not found. Drone movement won't be published to observers")
    dispatcher = None


class Drone(object):
    """
    A drone has coordinates, sensors, and a navigator. It is also capable of publishing messages to subsribers via
    PyDispatch. For example, in the future, it can be used for telemetry purposes to broadcast information back to
    mission control (via something like a zero-mq socket)
    """
    __slots__ = ['_coords', '_topology_sensors', '_navigator']

    # Signals that the drone broadcasts
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
        """
        The Navigator object used by the drone
        :return:
        """
        return self._navigator

    def move_to(self, point):
        """
        Moves the drone to the given 3d point. The movement might only care about the x and y values.
        In the future, the z value might be useful to know because of increased power use due to overcoming gravity
        We could also keep track of distance covered
        :param point: Point3D
        :return: point where actually moved (for now, same as input)
        """
        # Here we would actually move the drone. Note that in the future we might handle the case where the drone
        # does not succeed. For now, we'll just have it always succeed
        self._coords = point
        logging.info("Drone moved to " + repr(point))

        return point  # same as input for now

    def navigate_to_destination_point(self, start_point):
        """
        Navigates the drone to a a destination (e.g. extraction point)
        :param start_point: Where to begin, such as a beacon point
        :return: An ordered list of Point3D points that were navigated
        """
        logging.info("Start point is " + repr(start_point))
        self._coords = Point3D(start_point.x, start_point.y, 0)  # set start position without calling move_to

        # Notify any observers that the drone started
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
