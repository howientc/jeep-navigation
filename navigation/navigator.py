from geometry.point import Point3D


class Navigator(object):

    def __init__(self, topology_map, move_strategy, func_is_destination_point):
        self._topology_map = topology_map
        self._move_strategy = move_strategy
        self._func_is_destination_point = func_is_destination_point

    def iter_points_to_destination(self, start_point, topology_sensors):
        """
        Generates points as it navigates to an destination (e.g. extraction) point
        :param start_point: Where we are now
        :param topology_sensors: Sensor or sensors from the drone that are currently available
        :return: (generator) next point to visit. generator ends when destination point is found
        """
        point = start_point
        found = False
        while not found:  # keep generating points until done
            new_point, found = self._determine_next_point(point, topology_sensors)
            # Now that we know the previouis point's z, yield that point
            previous_point3d = Point3D(point.x, point.y, self._topology_map.get_z(point))
            yield previous_point3d
            point = new_point


    @staticmethod
    def choose_best_sensor(topology_sensors, adjacent_points):
        """
        Determines most efficient sensor to use. In case we have multiple sensors, we want to choose the wisest
        one to use for the points to be scanned. This could likely be a check to see which one is least costly to
        use for these points.
        Note that if the drone takes a sensor off line, it will no longer be in our list (which is a reference
        to the drone's list), so we won't use it by accident.
        :param topology_sensors: List of sensors available
        :param adjacent_points: The points that need to be scanned
        :return: The best sensor for the job
        """
        if len(topology_sensors) == 1:  # only 1 sensor, so use it
            return topology_sensors[0]

        # determine cheapest sensor by calling cost_to_scan on each
        cheapest_sensor = min(topology_sensors, key=lambda sensor: sensor.estimate_cost_to_scan(adjacent_points))
        return cheapest_sensor

    def _determine_next_point(self, point, topology_sensors):
        """
        Figures out what point to visit next. Will get information from a sensor and then look at the map to see
        if it's discovered an destination point. It also returns whether a destination was reached
        :param point: Point2D probably representing the current location
        :return: tuple(Point2D, bool): (Point2D where to go next, bool is whether this point is a destination point
        """
        tm = self._topology_map  # for convenience

        candidates = self._scan_and_get_destination_point_candidates(point, topology_sensors)

        # Now that we have our candidates, let's see if we've got a destination point
        for candidate_point in candidates:
            if self._func_is_destination_point(tm, candidate_point):
                return candidate_point, True  # Yes we found one.

        # What are the the directions to biggest points adjacent to where we are now?
        highest_directions = [(x, y) for x, y,_z, _pt in tm.list_highest_x_y_z_pt_in_radius(point)]

        next_point = self._move_strategy(tm, point, highest_directions)
        return next_point, False

    def _scan_and_get_destination_point_candidates(self, point, topology_sensors):
        """
        Figures out the points need to be scanned at and around the given point, then picks a sensor which does the job.
        Stores the sensor results in the topology map. In the process, determines which points are candidates for
        being destination points
        :param point:
        :param topology_sensors:
        :return: a list of candiates for being destination points
        """
        tm = self._topology_map  # for convenience

        # We will build up a set of cells that are candidates for being destination points.
        destination_candidates = set()
        destination_candidates.add(point)  # always need to check this point, even if we have its value already

        # x,y points below are from the perspective of center point is (0,0)
        # let's figure out what offsets we need to scan
        unknown_xy = tm.list_unknown_x_y_in_radius(point)

        if unknown_xy:  # Likely always true
            # if we've got many sensors, choose the best (cheapest) one for the job
            sensor = Navigator.choose_best_sensor(topology_sensors, unknown_xy)
            sensor.turn_on()
            sensor.increment_power_on_count()

            # ask the sensor to scan the unknown adjacent points. It might return MORE than what we asked for, so
            # we need to use the returned list as the scanned list. We'll only process those points that are newly
            # known on our topology_map
            scanned_points, scan_cost = sensor.scan_points(unknown_xy, point)
            for (_sx, _sy, sz, scanned_pt) in scanned_points:
                if not tm.get_z(scanned_pt):  # if the sensor returned a point we don't know, process it
                    tm.set_z(scanned_pt, sz)  # save value in our topology map
                    destination_candidates.add(scanned_pt)
                    # all unknown points adjacent to the scanned one are candidates too
                    # if scanned_pt != point:  # for all scans except original point, since we're handling it now
                    for _adj_x, _adj_y, adj_point in tm.iter_unknown_x_y_pt_in_radius(scanned_pt):
                        destination_candidates.add(adj_point)  # if might already be in thereif it was in scanned, which is fine

            sensor.turn_off()
        return list(destination_candidates)

