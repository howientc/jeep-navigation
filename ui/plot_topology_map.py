# https://matplotlib.org/gallery/frontpage/contour.html
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm


def plot_topology_map1(topology_map):
    # convert the x,y,z values into vectors x,y,z
    x, y, z = zip(*topology_map.walk_entire_map())
    X, Y = np.meshgrid(x,y)
    Z = np.asarray(z)
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())

    fig, ax = plt.subplots()
    cset1 = ax.contourf(
        X, Y, Z, 40,
        norm=norm)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    # fig.savefig("contour_frontpage.png", dpi=25)  # results in 160x120 px image
    plt.show()

def plot_topology_map2(topology_map):

    extent = (-3, 3, -3, 3)

    delta = 0.5
    x = np.arange(-3.0, 4.001, delta)
    y = np.arange(-4.0, 3.001, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = Z1 - Z2

    norm = cm.colors.Normalize(vmax=abs(Z).max(), vmin=-abs(Z).max())

    fig, ax = plt.subplots()
    cset1 = ax.contourf(
        X, Y, Z, 40,
        norm=norm)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    # fig.savefig("contour_frontpage.png", dpi=25)  # results in 160x120 px image
    plt.show()

def plot_topology_map(topology_map):
    # convert the x,y,z values into vectors x,y,z
    # x, y, z = zip(*topology_map.walk_entire_map())
    lower_left, top_right = topology_map.get_boundary_points()
    width, height = topology_map.width_and_height()

    grid = np.zeros((height, width))

    for x,y,z in topology_map.walk_entire_map():
        grid[x,y] = z

    fig, ax = plt.subplots()
    ax.imshow(X, interpolation='nearest')
    numrows, numcols = X.shape

    def format_coord(x, y):
        col = int(x + 0.5)
        row = int(y + 0.5)
        if col >= 0 and col < numcols and row >= 0 and row < numrows:
            z = X[row, col]
            return 'x=%1.4f, y=%1.4f, z=%1.4f' % (x, y, z)
        else:
            return 'x=%1.4f, y=%1.4f' % (x, y)

    ax.format_coord = format_coord
    plt.show()


# Fixing random state for reproducibility
# np.random.seed(19680801)

#
#
# X = 10*np.random.rand(5, 3)
#
# fig, ax = plt.subplots()
# ax.imshow(X, interpolation='nearest')
#
# numrows, numcols = X.shape
#
#
# def format_coord(x, y):
#     col = int(x + 0.5)
#     row = int(y + 0.5)
#     if col >= 0 and col < numcols and row >= 0 and row < numrows:
#         z = X[row, col]
#         return 'x=%1.4f, y=%1.4f, z=%1.4f' % (x, y, z)
#     else:
#         return 'x=%1.4f, y=%1.4f' % (x, y)
#
# ax.format_coord = format_coord
# plt.show()