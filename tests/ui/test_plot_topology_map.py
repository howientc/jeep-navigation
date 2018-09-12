from unittest import TestCase
from ui.plot_topology_map import plot_topology_map
from tests.topology.topology_factory import TopologyFactory
import random


class TestPlotTopologyMap(TestCase):

    def test_plot_topology_map(self):
        # Test whether we can actually plot the map
        random.seed(5)  # for testing, we want to always genereate same map
        tm = TopologyFactory.make_fake_topology()
        plot_topology_map(tm)  # unittest will catch any exception

