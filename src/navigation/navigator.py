from geometry.point import Point3D, Point2D
from topology.topology_map import TopologyMap
import logging

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
        self._found = None
        self._scan_costs = dict()


    @property
    def found(self):
        return self._found

    @property
    def scan_cost(self):
        return sum(self._scan_costs.values())

    def get_scan_cost_at_point(self, point):
        pt = Point2D(point.x, point.y)
        cost = self._scan_costs.get(pt, 0)
        return cost

    def set_scan_cost_at_point(self, point, value):
        pt = Point2D(point.x, point.y)
        self._scan_costs[pt] = value

    def reset(self):
        """
        Reset the navigator. Useful when testing
        """
        self._found = None
        self._topology_map = TopologyMap()
        self._scan_costs = dict()

    def set_move_strategy(self, move_strategy):
        self._move_strategy = move_strategy

    # def fill_path_to_destination(self, start_point, toppology_sensors):
    #     self._path = list(self.iter_points_to_destination(start_point, toppology_sensors))

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
        tm = self._topology_map
        point = start_point
        previous_point3d = None
        while not self._found:  # keep generating points until done
            new_point = self._determine_next_point(point, topology_sensors)

            # Now that we know the previouis point's z, yield that point
            previous_point3d = tm.make_3d(point)
            yield previous_point3d
            point = new_point

        # point = tm.make_3d(point)

        if point.z is  None:
            print("no z at ", point)
            print("found", self._found)

        if point.to_2d() != previous_point3d.to_2d():
            yield point

        # if point != self._found: # what we found might not have been visited yet
        #     print("also returning fond")
        #     yield self._found
        # else:
        #     print("skipping returning found", point, self._found)


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
                self._found = tm.make_3d(candidate_point)
                return self._found

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
        candidate_radius = 0
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
            self.set_scan_cost_at_point(point, scan_cost + sensor.power_on_cost)
            for (_sx, _sy, sz, scanned_pt) in scanned_points:
                if not tm.get_z(scanned_pt):  # if the sensor returned a point we don't know, save it
                    tm.set_z(scanned_pt, sz)
            sensor.turn_off()
            # As it turns out, we now have many points that we need to check for being destinations. These points
            # consist of all points in the scan radius, of course, and also, there could be points outside these bounds
            # whose "destination status" can now be determined because of these bounds being filled in. It turns out
            # that this radius is our sensor's radius + our destination radius
            candidate_radius = sensor.radius + self._destination.radius_needed_to_check
        else:
            logging.warning("No unknown points found for point", point)
        return [pt for _x, _y, _z, pt in tm.iter_x_y_z_pt_in_radius(point, radius=candidate_radius)]
