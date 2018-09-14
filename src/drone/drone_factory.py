# -*- coding: utf-8 -*-
"""
Factory class and helpers to simplify the creation of Drones
"""
from enum import Enum, auto
from navigation.navigator_factory import NavigatorFactory
from sensors.topology_sensor import TopologySensor
from topology.topology_map import TopologyMap
from drone.drone import Drone
from navigation.destinations import ExtractionPoint


class TopologySensorType(Enum):
    """
    These aren't used yet
    """
    Laser = auto()
    Radar = auto()


class DroneFactory(object):
    """
    Factory which creates drones through a static method
    """
    @staticmethod
    def make_sensor(sensor):
        """
        Makes a sensor if passed in an TopologySensorType.
        :param sensor: either a TopologySensorType or a TopologySensor
        """
        if isinstance(sensor, TopologySensor):
            return sensor

        # TODO Implement Laser, Radar...
        raise KeyError("Unknown Sensor Type: " + str(sensor))

    @staticmethod
    def make_drone(move_strategy, topology_sensors):
        """
        Makes a drone (factory method). Accepts either objects or Enums as arguments.
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

        destination = ExtractionPoint()
        navigator = NavigatorFactory.make_navigator(topology_map=topology_map,
                                                    move_strategy=move_strategy,
                                                    destination=destination)

        return Drone(navigator, topology_sensors=sensors)
