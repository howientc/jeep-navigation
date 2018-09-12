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
        while True:  # keep generating points until done
            point, found = self._determine_next_point(point, topology_sensors)
            yield point
            if found:
                break

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
        Figures out where to go next. Will get information from a sensor and then look at the map to see
        if it's discovered an destination point.
        :param point: Point2D probably representing the current location
        :return: tuple(Point2D, bool): (Where to go next, bool is whether this point is an destination point
        """
        tm = self._topology_map  # for convenience
        candidates = self._scan_and_get_destination_point_candidates(point, topology_sensors)

        # Now that we have our candidates, let's see if we've got a destination point
        for candidate_point in candidates:
            if self._func_is_destination_point(tm, candidate_point):
                return candidate_point, True  # Yes we found one.

        # What are the the directions to biggest points adjacent to where we are now?
        highest_directions = tm.get_highest_adjacent_points_as_directions(point)

        next_point = self._move_strategy.determine_next_point(tm, point, highest_directions)
        return next_point, False

    def _scan_and_get_destination_point_candidates(self, point, topology_sensors):
        """
        Figures out what points need to be scanned around the given point, then picks a sensor which does the job.
        Stores the sensor results in the topology map. In the process, determines which points are candidates for
        being destination points
        :param point:
        :param topology_sensors:
        :return:
        """
        tm = self._topology_map  # for convenience

        # We will build up a set of cells that are candidates for being destination points.
        candidates = set()
        candidates.add(point)  # the current point is a candidate

        # let's figure out what points we need to scan
        unknown_adjacent_points = tm.unknown_adjacent_points(point)

        if unknown_adjacent_points:  # if we need to scan. Most of time we will

            # if we've got many sensors, choose the best (cheapest) one for the job
            sensor = Navigator.choose_best_sensor(topology_sensors, unknown_adjacent_points)
            sensor.turn_on()
            sensor.increment_power_on_count()

            # ask the sensor to scan the unknown adjacent points. It might return MORE than what we asked for, so
            # we need to use the returned list as the scanned list. We'll only process those points that are newly
            # known on our topology_map
            scanned_points = sensor.scan_points(unknown_adjacent_points, point)
            for x, y, z, scanned_pt in scanned_points:
                if not tm.get_z(scanned_pt):  # if the sensor returned a point we already know, skip it
                    tm.set_z(scanned_pt, z)  # save value in our topology map
                    candidates.add(scanned_pt)
                    # all points adjacent to the scanned one are candidates too
                    for _x, _y, _z, adj_point in tm.walk_adjacent(scanned_pt):
                        candidates.add(adj_point)

            sensor.turn_off()
        return candidates

