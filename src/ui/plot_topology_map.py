import matplotlib.pyplot as plt
import numpy as np
import math


def draw_path(path):
    """
    Plot the path. The start and end will have special styling
    :param path:
    :return:
    """
    # Plot start point
    start_x, start_y, start_z = path[0]
    plt.plot(start_x, start_y, 'ws')  # start is a white square

    # Plot middle points
    if len(path) > 2:
        x_vals, y_vals, _z_vals = zip(*path)  # convert into X,Y,Z arrays
        plt.plot(x_vals[1:-1], y_vals[1:-1], 'mo')  # remove head and tail in plot magenta circles

    # Plot end points
    end_x, end_y, end_z = path[-1]
    plt.plot(end_x, end_y, 'r^')  # endpoint is a red diamond


def plot_topology_map(topology_map, func_get_path):
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

    def on_click(event):
        """
        Calculates and displays new path from cicked point
        :param event:
        :return:
        """
        plt.cla()
        ax.imshow(grid, origin='lower', extent=extent)
        # get closes integer points
        cx = math.floor(round(event.xdata))
        cy = math.floor(round(event.ydata))

        path = func_get_path(cx, cy)  # get a new path from the click origin
        draw_path(path)
        plt.title("Start:({},{}), Destination: ({},{})".format(cx, cy, path[-1][0], path[-1][1]))

        fig.canvas.draw()

    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    plt.title("Click a point to navigate from it to high ground")
    fig.canvas.set_window_title("Plot Path Example")
    plt.show()
    # I am not sure how to get rid of that toolbar
