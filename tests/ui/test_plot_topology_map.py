from unittest import TestCase
from ui.plot_topology_map import plot_topology_map
from tests.topology.simulate_topology import generate_random_topology

class TestPlotTopologyMap(TestCase):

    def test_plot_topology_map(self):
        # Test whether we can actually plot the map
        tm = generate_random_topology()
        plot_topology_map(tm)  # unittest will catch any exception

