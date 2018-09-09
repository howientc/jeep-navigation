from enum import Enum, auto
from navigation.move_one_strategy import MoveOneStrategy
from navigation.move_sensor_width_strategy import MoveSensorWidthStrategy
from navigation.navigation_strategy import NavigationStrategy
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
    def make_topology_sensor(topology_sensor_type):
        """
        Factory method to make a topology sensor. If we wind up with lots of them,
        maybe move to a factory class
        """
        # TODO Implement Laser, Radar...
        raise KeyError("Unknown Sensor Type: " + str(topology_sensor_type))

    @staticmethod
    def make_drone(navigation_strategy, topology_sensor):
        """
        Factory method to make a drone. Accepts either objects or Enums as arguments
        :param navigation_strategy: either a Navigation strategy, or Enum NavigationStrategyType
        :param topology_sensor: either a TopologySensor, or Enum TopologySensorType
        :return:
        """

        # Map of known areas of the topology. In the future, we could persist this map and then
        # reuse it for this or any drone on subsequent missions
        topology_map = TopologyMap()

        if not isinstance(navigation_strategy, NavigationStrategy):
            navigation_strategy = DroneFactory.make_navigation_strategy(navigation_strategy)

        if not isinstance(topology_sensor, TopologySensor):
            topology_sensor = DroneFactory.make_topology_sensor(topology_sensor)

        # inject the map into both the strategy and the sensor
        navigation_strategy.set_topology_map(topology_map)
        topology_sensor.set_topology_map(topology_map)

        return Drone(navigation_strategy=DroneFactory.make_navigation_strategy(navigation_strategy),
                     topology_sensor=DroneFactory.make_topology_sensor(topology_sensor))
