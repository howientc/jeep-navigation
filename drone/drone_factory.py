from enum import Enum, auto
from navigation.navigation import Navigation
from navigation.navigation_strategies import NavigationStrategy
from sensors.topology_sensor import TopologySensor
from topology.topology_map import TopologyMap
from drone.drone import Drone


# These enums will be passed into clients of the factory
class NavigationStrategyType(Enum):
    MoveOne = auto()
    MoveSensorWidth = auto()


class TopologySensorType(Enum):
    """
    These aren't used yet
    """
    Laser = auto()
    Radar = auto()


class DroneFactory(object):
    @staticmethod
    def make_navigation_strategy(navigation_strategy_type):
        """
        Factory method to make a navigation strategy. If we wind up with lots of them,
        maybe move to a factory class
        :param navigation_strategy_type:
        :return: NavigationStrategy instance
        """
        if navigation_strategy_type == NavigationStrategyType.MoveOne:
            return MoveOneStrategy()
        elif navigation_strategy_type == NavigationStrategyType.MoveSensorWidth:
            return MoveSensorWidthStrategy()
        else:
            raise KeyError("Unknown Strategy Type: " + str(navigation_strategy_type))

    @staticmethod
    def make_sensor(sensor):
        """
        Factory method to make a topology sensor.
        """
        if isinstance(sensor, TopologySensor):
            return sensor

        # TODO Implement Laser, Radar...
        raise KeyError("Unknown Sensor Type: " + str(topology_sensor_type))

    @staticmethod
    def is_extraction_point_func():
        """
        For flexibility, this provides a means to specify a rule for determining if a point is an extraction point.
        This can be useful if the definition of extraction point can depend on something. For example, in bad
        weather, we might redefine an extraction point to one having a plateau of a size larger than 1. For now,
        just use standard definition, that an extraction point cell is higher (or equal to) its adjacent cells
        :return:
        """
        def highest_of_adjacent(topology_map, point):
            """
            Local method to hold a callback to the standard test test
            :param topology_map:
            :param point:
            :return:
            """
            return topology_map.is_highest_of_cached_adjacent(point)

        return highest_of_adjacent

    @staticmethod
    def make_drone(navigation_strategy, topology_sensors):
        """
        Factory method to make a drone. Accepts either objects or Enums as arguments.
        This uses an Dependency Injection pattern for flexibility. We can use a variety of sensors,
        navigation strategies, and rules, and then we pass the chosen ones the dependencies they need,
        for example, the topology map is needed by everyone.
        :param navigation_strategy: either a Navigation strategy, or Enum NavigationStrategyType
        :param topology_sensors: a list containing elements of either TopologySensor, or Enum TopologySensorType
        :return:
        """

        # Map of known areas of the topology. In the future, we could persist this map and then
        # reuse it for this or any drone on subsequent missions
        topology_map = TopologyMap()

        navigation_strategy = DroneFactory.make_navigation_strategy(navigation_strategy)

        # convert the passed-in sensor list to actual sensors in case enums were passed in
        sensors = [s if isinstance(s, TopologySensor) else DroneFactory.make_sensor(s) for s in topology_sensors]

        navigation_strategy = DroneFactory.make_navigation_strategy(navigation_strategy)
        is_extraction_point_func = DroneFactory.is_extraction_point_func()
        navigation = Navigation(topology_map=topology_map,
                                navigation_strategy=navigation_strategy,
                                is_extraction_point_func=is_extraction_point_func)

        return Drone(navigation, topology_sensors=sensors)
