from unittest import TestCase
from ui.plot_topology_map import plot_topology_map
from tests.topology.simulated_topology import SimulatedTopology
from tests.topology.test_simulated_topology import TEST_MAP

class TestPlotTopology_map(TestCase):
    def test_plot_topology_map(self):
        top = SimulatedTopology(TEST_MAP)
        plot_topology_map(top)
