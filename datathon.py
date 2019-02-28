"""
The datathon package is a collection of helper functions used when running datathons.
"""

__version__ = "0.1.0"

import pandas as pd
import numpy as np

from sklearn import tree

import pydotplus
import matplotlib
import matplotlib.pyplot as plt
from IPython.display import Image


def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return matplotlib.colors.LinearSegmentedColormap('CustomMap', cdict)


def plot_model_pred_2d(mdl, X, y,
                       cm=None, cbar=True, xlabel=None, ylabel=None):
    """
    For a 2D dataset, plot the decision surface of a tree model.
    """
    # look at the regions in a 2d plot
    # based on scikit-learn tutorial plot_iris.html

    # get minimum and maximum values
    x0_min = X[:, 0].min()
    x0_max = X[:, 0].max()
    x1_min = X[:, 1].min()
    x1_max = X[:, 1].max()

    xx, yy = np.meshgrid(np.linspace(x0_min, x0_max, 100),
                         np.linspace(x1_min, x1_max, 100))

    Z = mdl.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    if not cm:
        # custom colormap
        # e58139f9 - orange
        # 399de5e0 - to blue
        s = list()

        lo = np.array(matplotlib.colors.to_rgb('#e5813900'))
        hi = np.array(matplotlib.colors.to_rgb('#399de5e0'))

        for i in range(255):
            s.append(list((hi-lo)*(float(i)/255)+lo))
        cm = make_colormap(s)

    # plot the contour - colouring different regions
    plt.contourf(xx, yy, Z, cmap=cm)

    # plot the individual data points - colouring by the *true* outcome
    color = y.ravel()
    plt.scatter(X[:, 0], X[:, 1], c=color, edgecolor='k', linewidth=2,
                marker='o', s=60, cmap=cm)

    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.axis("tight")
    # plt.clim([-1.5,1.5])
    if cbar:
        plt.colorbar()


def create_graph(mdl, feature_names=None, cmap=None):
    """
    Display a graph of the decision tree.

    cmap is a colormap
    e.g.
      cmap = np.linspace(0.0, 1.0, 256, dtype=float)
      cmap = matplotlib.cm.coolwarm(cmap)
    """
    tree_graph = tree.export_graphviz(mdl, out_file=None,
                                      feature_names=feature_names,
                                      filled=True, rounded=True)
    graph = pydotplus.graphviz.graph_from_dot_data(tree_graph)

    # get colormap
    if cmap:
        # remove transparency
        if cmap.shape[1] == 4:
            cmap = cmap[:, 0:2]

        nodes = graph.get_node_list()
        for node in nodes:
            if node.get_label():
                # get number of samples in group 1 and group 2
                num_samples = [int(ii) for ii in node.get_label().split(
                    'value = [')[1].split(']')[0].split(',')]

                # proportion that is class 2
                cm_value = float(num_samples[1]) / float(sum(num_samples))
                # convert to (R, G, B, alpha) tuple
                cm_value = matplotlib.cm.coolwarm(cm_value)
                cm_value = [int(np.ceil(255*x)) for x in cm_value]
                color = '#{:02x}{:02x}{:02x}'.format(
                    cm_value[0], cm_value[1], cm_value[2])
                node.set_fillcolor(color)

    Image(graph.create_png())
    return graph


def prune(dt, min_samples_leaf=1):
    """
    Implicitly prune model by setting node children to -1.
    Note: displaying the graph will still show all nodes.
    """
    # Pruning is done by the "min_samples_leaf" property of decision trees
    if dt.min_samples_leaf >= min_samples_leaf:
        print('Decision tree is pruned at an equal or higher level.')
    else:
        # update prune parameter
        dt.min_samples_leaf = min_samples_leaf

        # loop through each node of the tree
        tree = dt.tree_
        for i in range(tree.node_count):
            n_samples = tree.n_node_samples[i]
            if n_samples <= min_samples_leaf:
                # we can't delete splits because they are fixed in the model
                # instead, we remove the split by setting the child values to -1
                tree.children_left[i] = -1
                tree.children_right[i] = -1
