import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.figure import Figure

FONT_SIZE = 40


class MyFigure(Figure):
    def __init__(self, *args, **kwargs):
        """
        custom kwarg figtitle is a figure title
        """
        figtitle = kwargs.pop('figtitle', 'hi mom')
        Figure.__init__(self, *args, **kwargs)
        self.text(0.5, 0.95, figtitle, ha='center')


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

    figtitle = "Path is numbered in order of visitation. From white square to red triangle\n" \
    "The triangle will have red text if it didn't need to be scanned\n" \
    "Press the space bar to cycle through strategies, or click a new point"

    fig = plt.figure(FigureClass=MyFigure, figtitle=figtitle)
    ax = fig.subplots()
    # fig, ax = plt.subplots()

    # To center axes labels with cells, enlarge the extent by half a cell width on all sides
    extent = (lower_left.x - .5, upper_right.x + .5, lower_left.y - .5, upper_right.y + .5)
    ax.imshow(grid, origin='lower', extent=extent)


    def draw_path(path):
        font_size = FONT_SIZE // 2
        symbol_size = FONT_SIZE * 0.75
        # Plot start point
        start_x, start_y, start_z, start_cost = path[0]
        plt.plot(start_x, start_y, 'wo', markersize=symbol_size)  # start is a white circle

        # Plot end points
        end_x, end_y, end_z, end_cost = path[-1]
        plt.plot(end_x, end_y, 'r^', markersize=symbol_size)  # endpoint is a red diamond

        offset = .2
        for i, point in enumerate(path):
            color = "blue" if point[3] else "white"  # scanned here
            plt.text(point[0] - offset, point[1] - offset, str(i), color=color, fontsize=FONT_SIZE // 2)


    def replot(cx, cy, change=False):
        plt.cla()
        ax.imshow(grid, origin='lower', extent=extent)

        path, strategy_name = func_get_path(cx, cy, change)  # get a new path from the click origin
        if not path:
            return
        draw_path(path)

        cost = 0
        scans = 0
        for p in path:
            cost += p[3]
            if p[3]:
                scans += 1

        plt.title("{} strategy\n({},{}),=> ({},{})\nScans: {} Cost: {}".
                  format(strategy_name, path[0][0], path[0][1], path[-1][0], path[-1][1], scans, cost))

        fig.canvas.draw()


    def on_click(event):
        if not event.xdata or not event.ydata:
            return
        # get closes integer points
        cx = math.floor(round(event.xdata))
        cy = math.floor(round(event.ydata))
        replot(cx, cy)


    cid = fig.canvas.mpl_connect('button_press_event', on_click)

    def on_key(event):
        if event.key ==' ':
            replot(0, 0, True)

    cid = fig.canvas.mpl_connect('key_press_event', on_key)

    plt.title("Click a point to navigate from it to high ground")
    # plt.legend("BLue text = a scan was done at that spot")
    fig.canvas.set_window_title("Plot Path Example")

    # make window big
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())

    plt.show()
    # I am not sure how to get rid of that toolbar
