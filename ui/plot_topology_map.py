# https://matplotlib.org/gallery/frontpage/contour.html
import matplotlib.pyplot as plt
import numpy as np


def plot_topology_map(topology_map):
    """
    Plots the map with color coding for heights
    :param topology_map:
    :return:
    """
    lower_left, upper_right = topology_map.boundary_points
    width, height = topology_map.width_and_height
    grid = np.zeros((height, width))

    # populate the grid with our topology
    for x, y, z in topology_map.iter_all_points_xyz():
        # normalize each point so that the lower left point is on 0,0
        normalized_x = x - lower_left.x
        normalized_y = y - lower_left.y
        grid[normalized_y, normalized_x] = z  # grid is indexed by rows(y) first, not columns(x)
    fig, ax = plt.subplots()

    # To center axes labels with cells, enlarge the extent by half a cell width on all sides
    extent = (lower_left.x - .5, upper_right.x + .5, lower_left.y - .5, upper_right.y + .5)
    ax.imshow(grid, origin='lower', extent=extent)
    plt.show()
