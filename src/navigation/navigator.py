from geometry.point import Point3D
from topology.topology_map import TopologyMap


class Navigator(object):

    def __init__(self, topology_map, move_strategy, destination):
        """
        :param topology_map:
        :param move_strategy:
        :param destination: Destination object
        """
        self._topology_map = topology_map
        self._move_strategy = move_strategy
        self._destination = destination
        self._path = []
        self._found = None

    @property
    def path(self):
        return self._path

    @property
    def found(self):
        return self._found

    def reset(self):
        self._path = []
        self._found = None
        self._topology_map = TopologyMap()

    def iter_points_to_destination(self, start_point, topology_sensors):
        """
        Generates points as it navigates to an destination (e.g. extraction) point. Because this is
        a generator, it just produces a series of points without any check whether we successfully moved
        to those points. A potential problem to address in the future is if our drone is not successful
        in moving to the requested point and winds up somewhere else. We would need a way to get that information
        back here. Consider refactoring to use using a callback argument "func_move" instead of using a generator.
        This "func_move" will will be passed the point to move to, and will return the point it actually moved to so,
        we can update our navigation accordingly.
        :param start_point: Where we are now
        :param topology_sensors: Sensor or sensors from the drone that are currently available
        :return: (generator) next point to visit. generator ends when destination point is found
        """
        self.reset()  # in case we're recycling the navigator

        point = start_point
        while not self._found:  # keep generating points until done
            new_point = self._determine_next_point(point, topology_sensors)

            # Now that we know the previouis point's z, yield that point
            previous_point3d = Point3D(point.x, point.y, self._topology_map.get_z(point))
            self.path.append(previous_point3d)  # keep track of path
            yield previous_point3d
            point = new_point

        yield Point3D(point.x, point.y, self._topology_map.get_z(point))
        if point != self._found: # what we found might not have been visited yet
            yield self._found


        # self.reset()  # in case we're recycling the navigator
        #
        # point = start_point
        # found = False
        # while not found:  # keep generating points until done
        #     new_point, found = self._determine_next_point(point, topology_sensors)
        #     # Now that we know the previouis point's z, yield that point
        #     previous_point3d = Point3D(point.x, point.y, self._topology_map.get_z(point))
        #     self.path.append(previous_point3d)  # keep track of path
        #     yield previous_point3d
        #     point = new_point
        # # need to yield the last value
        # yield Point3D(point.x, point.y, self._topology_map.get_z(point))
        # self._found = point

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
        if it's discovered an destination point. If so, it sets the _found member. In any case, it returns the next
        point to visit
        :param point: Point2D probably representing the current location
        :return: Point2D: (Point2D where to go next/
        """
        tm = self._topology_map  # for convenience

        candidates = self._scan_and_get_destination_point_candidates(point, topology_sensors)

        # Now that we have our candidates, let's see if we've got a destination point
        for candidate_point in candidates:
            if self._destination(tm, candidate_point):
                print("Found ", candidate_point)
                self._found = candidate_point
                break

        next_point = self._move_strategy(tm, point, self._destination)
        return next_point

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

        # x,y points below are from the perspective of center point is (0,0)
        # let's figure out what offsets we need to scan
        unknown_xy = tm.list_unknown_x_y_in_radius(point, self._destination.radius_needed_to_check)
        sensor = None
        if unknown_xy:  # Likely always true
            # if we've got many sensors, choose the best (cheapest) one for the job
            sensor = Navigator.choose_best_sensor(topology_sensors, unknown_xy)
            if not sensor:
                raise Exception("No sensor is available")
            sensor.turn_on()
            sensor.increment_power_on_count()

            # ask the sensor to scan the unknown adjacent points. It might return MORE than what we asked for, so
            # we need to use the returned list as the scanned list.
            scanned_points, scan_cost = sensor.scan_points(unknown_xy, point)
            for (_sx, _sy, sz, scanned_pt) in scanned_points:
                if not tm.get_z(scanned_pt):  # if the sensor returned a point we don't know, save it
                    tm.set_z(scanned_pt, sz)

            sensor.turn_off()

        # As it turns out, we now have many points that we need to check for being destinations. These points
        # consist of all points in the scan radius, of course, and also, there could be points outside these bounds
        # whose "destination status" can now be determined because of these bounds being filled in. It turns out
        # that this radius is our sensor's radius + our destination radius
        candidate_radius = sensor.radius + self._destination.radius_needed_to_check
        return [pt for _x, _y, _z, pt in tm.iter_x_y_z_pt_in_radius(point, radius=candidate_radius)]