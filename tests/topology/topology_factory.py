from topology.topology_map import TopologyMap
from geometry.point import Point2D, Point3D, ORIGIN
import random


class TopologyFactory(object):
    def __init__(self, lower_left, upper_right):
        self._lower_left = lower_left
        self._upper_right = upper_right
        self._tm = TopologyMap()

    @property
    def cell_count(self):
        return (self._upper_right.x - self._lower_left.x + 1) * (self._upper_right.y - self._lower_left.y + 1)

    def add_peaks_from_seed_points3d(self, seed_points_3d, style='cone', steepness=1):
        """
        The seed points are local or global maximums, and then
        surrounding points are lower and lower with distance. 'cone' style has peaks shaped like cones,
        'pyramid' style shapes them like 4 sided pyramids. Note that where peaks would collide, the valleys
        are not smoothed. It is possible to have more "extraction points" (summits or flat areas) than given
        in the seeds due to the way the peaks collide

        :param steepness: Height of step between adjacent cells
        :param seed_points_3d: e.g. [Point3D(15,6,69), Point3D(21,11,52), Point3D(3, 4, 34)]
        :param style: 'cone' or 'pyramid' which determines curve shape
        :return: self (to allow chaining)
        """
        if style == 'cone':
            z_func = Point2D.distance2d
        elif style == 'pyramid':
            z_func = Point2D.max_orthogonal_distance
        else:
            raise Exception('Unknown Style:' + style)

        # Go through all points. Pick the closest seed to the point, and calculate its z value and insert it
        for y in range(self._lower_left.y, self._upper_right.y + 1):
            for x in range(self._lower_left.x, self._upper_right.x + 1):
                grid_point = Point2D(x, y)
                closest_seed = min(seed_points_3d, key=lambda seed: grid_point.distance2d(seed))
                delta_z = round(steepness * (closest_seed.z - z_func(grid_point, closest_seed)))
                if delta_z < 0:
                    delta_z = 0
                # get existing value if any for this point (in case adding a layer)
                z = self._tm.get_z(grid_point,
                                   default=0)
                self._tm.set_z(Point2D(x, y), z + delta_z)

        return self._tm

    def random_points_3d(self, number_of_seeds, min_z, max_z):
        """
        Creates a list of unique (x,y,z) tuples
        :param number_of_seeds: Number of unique points to generate
        :param min_z: Minimum z value to generate
        :param max_z: Maximum z value to generate
        :return:
        """
        # Sanity check. We can't get more seeds than what's available in the bounds
        assert number_of_seeds <= self.cell_count

        found = {}
        while len(found) < number_of_seeds:
            pt = Point2D(random.randint(self._lower_left.x, self._upper_right.x),
                         random.randint(self._lower_left.y, self._upper_right.y))
            if pt not in found:  # make sure unique
                found[pt] = random.randint(min_z, max_z)
        return [Point3D(pt.x, pt.y, z) for pt, z in found.items()]

    @staticmethod
    def make_fake_topology(density=.03, lower_left=ORIGIN, upper_right=Point2D(30, 30), max_z=None):
        """
        Generates a topology to test with. It's possible that the resulting topology could have more "extraction points"
        (peaks or flat areas) than the number of seeds because of the way the generated peaks collide.
        :param density: number of peeks / total area
        :param lower_left: lower-left point
        :param upper_right: upper-right point
        :param max_z: Maximum z value to generate
        :return: generated topology map
        """
        styles = ['cone', 'pyramid']
        if not max_z:
            biggest_axis = max(upper_right.x - lower_left.x, upper_right.y - lower_left.y)
            max_z = round(biggest_axis / 1.2)  # Just need a rule here. how about max height is half width?

        factory = TopologyFactory(lower_left, upper_right)
        number_of_seeds = round(factory.cell_count * density)  # how many seeds depends on density and area

        # Produce roughly (due to rounding) the number of seeds. We will perform multiple passes,
        # generating random x,y,z values and adding them as peaks on the map. With each pass, the
        # range of z values tends to get smaller (though there is randomness).
        # Also, each pass has a random steepness value, which is essentially the step height if we
        # are walking up an Aztec pyramid
        seeds_per_pass = 5  # a decent-looking value
        passes = round(number_of_seeds // seeds_per_pass)

        for i in range(1, passes + 1):
            # get a z-range for this pass
            max_z_pass = round(max_z / i)
            min_z_pass = max_z_pass // 2

            seeds = factory.random_points_3d(seeds_per_pass, min_z_pass, max_z_pass)
            steepness = random.uniform(1, 4)  # the resulting step height between adjacent cells
            factory.add_peaks_from_seed_points3d(seeds, random.choice(styles), steepness=steepness)
        return factory._tm
