import matplotlib.pyplot as plt
import numpy as np
import math

#
# def draw_path(ax, path):
#     """
#     Plot the path. The start and end will have special styling
#     :param path:
#     :return:
#     """
#     # Plot start point
#     # start_x, start_y, start_z = path[0]
#     # plt.plot(start_x, start_y, 'ws')  # start is a white square
#     #
#     # # Plot middle points
#     # if len(path) > 2:
#     #     x_vals, y_vals, _z_vals = zip(*path)  # convert into X,Y,Z arrays
#     #     plt.plot(x_vals[1:-1], y_vals[1:-1], 'mo')  # remove head and tail in plot magenta circles
#     #
#     # # Plot end points
#     # end_x, end_y, end_z = path[-1]
#     # plt.plot(end_x, end_y, 'r^')  # endpoint is a red diamond
#
#     offset = .25
#     for i, point in enumerate(path):
#         plt.text(point[0]-offset, point[1]-offset, str(i), fontsize=12)


FONT_SIZE=40
def plot_topology_map(topology_map, func_get_path):
    """
    Plots the map with color coding for heights
    :param topology_map:
    :return:
    """

    plt.rcParams.update({'font.size': FONT_SIZE * 0.6})

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

    def draw_path(path):
        font_size = FONT_SIZE//2
        symbol_size = FONT_SIZE * 0.75
            # Plot start point
        start_x, start_y, start_z, start_cost = path[0]
        plt.plot(start_x, start_y, 'wo',markersize=symbol_size)  # start is a white circle

        # Plot end points
        end_x, end_y, end_z, end_cost = path[-1]
        plt.plot(end_x, end_y, 'r^',markersize=symbol_size)  # endpoint is a red diamond

        offset = .2
        for i, point in enumerate(path):
            print("scan cost", point[3])
            color = "blue" if point[3] else "white"  # scanned here
            plt.text(point[0] - offset, point[1] - offset, str(i), color=color, fontsize=FONT_SIZE//2)

    def on_click(event):
        """
        Calculates and displays new path from cicked point
        :param event:
        :return:
        """
        if not event.xdata or not event.ydata:
            return
        plt.cla()
        ax.imshow(grid, origin='lower', extent=extent)
        # get closes integer points
        cx = math.floor(round(event.xdata))
        cy = math.floor(round(event.ydata))

        path = func_get_path(cx, cy)  # get a new path from the click origin
        draw_path(path)

        cost = 0
        scans = 0
        for p in path:
            cost += p[3]
            if p[3]:
                scans += 1

        plt.title("Start:({},{}), Destination: ({},{}) Scans: {} Cost: {}".
                  format(cx, cy, path[-1][0], path[-1][1],scans,cost))

        fig.canvas.draw()

    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    plt.title("Click a point to navigate from it to high ground")
    plt.legend("BLue text = a scan was done at that spot")
    fig.canvas.set_window_title("Plot Path Example")

    # make window big
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())

    plt.show()
    # I am not sure how to get rid of that toolbar
