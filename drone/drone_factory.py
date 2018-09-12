from enum import Enum, auto
from navigation.navigator_factory import NavigatorFactory
from sensors.topology_sensor import TopologySensor
from topology.topology_map import TopologyMap
from drone.drone import Drone


class TopologySensorType(Enum):
    """
    These aren't used yet
    """
    Laser = auto()
    Radar = auto()


class DroneFactory(object):

    @staticmethod
    def make_sensor(sensor):
        """
        Factory method to make a topology sensor.
        """
        if isinstance(sensor, TopologySensor):
            return sensor

        # TODO Implement Laser, Radar...
        raise KeyError("Unknown Sensor Type: " + str(sensor))

    @staticmethod
    def func_is_extraction_point():
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
            return topology_map.is_highest_of_known_adjacent(point)

        return highest_of_adjacent

    @staticmethod
    def make_drone(move_strategy, topology_sensors):
        """
        Factory method to make a drone. Accepts either objects or Enums as arguments.
        We can use a variety of sensors, navigation strategies, and rules, and then we pass the chosen ones
        the dependencies they need,
        For example, the topology map is needed by everyone.
        :param move_strategy: either a MoveStrategy, a function, or Enum NavigationStrategyType
        :param topology_sensors: a list containing elements of either TopologySensor, or Enum TopologySensorType
        :return:
        """

        # Map of known areas of the topology. In the future, we could persist this map and then
        # reuse it for this or any drone on subsequent missions
        topology_map = TopologyMap()

        # convert the passed-in sensor list to actual sensors in case enums were passed in
        sensors = [s if isinstance(s, TopologySensor) else DroneFactory.make_sensor(s) for s in topology_sensors]

        func_is_destination_point = DroneFactory.func_is_extraction_point()
        navigator = NavigatorFactory.make_navigator(topology_map=topology_map,
                                                    move_strategy=move_strategy,
                                                    func_is_destination_point=func_is_destination_point)

        return Drone(navigator, topology_sensors=sensors)
