class Navigation(object):

    def __init__(self, topology_map, navigation_strategy, is_extraction_point_func):
        self._topology_map = topology_map  # will be injected later by factory
        self._navigation_strategy = navigation_strategy
        self._is_extraction_point_func = is_extraction_point_func

    def navigate_to_extraction_point(self, start_point, topology_sensors, move_callback=None):
        """
        :param start_point:
        :param topology_sensors: Sensor or sensors from the drone that are currently available
        :param move_callback: a function to call with the current point so as to move to it
        :return:
        """
        found = False
        point = start_point
        while not found:
            point, done = self._determine_next_point(point, topology_sensors)
            if move_callback:
                move_callback(point)

    def _determine_next_point(self, point, topology_sensors):
        """
        :param point:
        :return: tuple(Point, bool) Point is where to go next, bool is whether this point is an extraction point
        """
        tm = self._topology_map  # for convenience
        candidates = self._scan_and_get_candidates(point, topology_sensors)

        # Now that we have our candidates, let's see if we've got an extraction point
        for candidate_point in candidates:
            if self.is_extraction_point_func(tm,candidate_point):
                return candidate_point, True  # Yes we found one.

        # What are the biggest points adjacent to where we are now?
        highest_offsets = tm.get_highest_adjacent_points_as_offsets(point)

        next_point = self._navigation_strategy.determine_next_point(tm, point, highest_offsets)
        return next_point, False

    def _scan_and_get_candidates(self, point, topology_sensors):
        tm = self._topology_map  # for convenience

        # We will build up a set of cells that are candidates for being extraction points.
        candidates = set()
        candidates.add(point)  # the current point is a candidate

        # let's figure out what points we need to scan
        unknown_adjacent_points = tm.unknown_adjacent_points(point)

        if unknown_adjacent_points: # if we need to scan. Most of time we will

            # if we've got many sensors, choose the best (cheapest) one for the job
            sensor = self._choose_best_sensor(topology_sensors, unknown_adjacent_points)
            sensor.turn_on()
            sensor.increment_power_on_count()

            # ask the sensor to scan the unknown adjacent points. It might return MORE than what we asked for, so
            # we need to use the returned list as the scanned list. We'll only process those points that are newly
            # known on our topology_map
            scanned_points = sensor.scan_points(unknown_adjacent_points, point)
            for x, y, z, scanned_pt in scanned_points:
                if not tm.get_z(scanned_pt): # if the sensor returned a point we already know, skip it
                    tm.set_z(scanned_pt, z)  # save value in our topology map
                    candidates.add(scanned_pt)
                    # all points adjacent to the scanned one are candidates too
                    for _x, _y, _z, adj_point in tm.walk_adjacent(scanned_pt):
                        candidates.add_point(adj_point)

            sensor.turn_off()
        return candidates

    def _choose_best_sensor(self, topology_sensors, adjacent_points):
        """
        In case we have multiple sensors, we want to choose the wisest one to use for the points to be
        scanned. This could likely be a check to see which one is least costly to use for these points.
        Note that if the drone takes a sensor off line, it will no longer be in our list (which is a reference
        to the drone's list), so we won't use it by accident.
        :param unknown_adjacent_points:
        :return:
        """
        if len(topology_sensors) == 1:  # only 1 sensor, so use it
            return topology_sensors[0]

        # determine cheapest sensor by calling cost_to_scan on each
        cheapest_sensor = min(topology_sensors, key=lambda sensor: sensor.estimate_cost_to_scan(adjacent_points))
        return cheapest_sensor


