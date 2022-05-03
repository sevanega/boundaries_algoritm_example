"""
A module for processing networkx graphs
"""
import pandas as pd
import networkx as nx
from networkx.algorithms.tree import minimum_spanning_tree
from boundaries_algorithm.validation.poly_module import (
    convex_hull,
    get_buffer_area,
)


def mst(arcs, node_attributes):
    """Returns de minimum spannning tree (MST) of a list of arcs
    
    The funtion uses de networkx package and specifically
    the minimum_spanning_tree function with the default
    Kruskal's algorithm

    Parameters
    ----------
    arcs : tuple
        tuple containing (u, v, w)
    node_attributes : dict
        dictionary with nodes as keys and attributes as values
        

    Returns
    -------

    
    """
    G = nx.Graph()
    G.add_weighted_edges_from(arcs)
    T = minimum_spanning_tree(G, weight="weight")
    nx.set_node_attributes(T, node_attributes, name="xy")
    return T


def all_rmc_mean(main_G):
    """Computes the mean of all shortest path in a graph for
    node
    
    Function returns a pandas.core.series.Series with nodes
    and mean shortest path lengths between all nodes in a
    weighted graph using shortest path networkx funtion
    all_pairs_dijkstra_path_length

    Parameters
    ----------
    main_G : networkx.classes.graph.Graph
        A networkx Graph object with nodes
        and weighted arcs

    Returns
    -------

    
    """
    copy_G = main_G.copy()
    rmc = dict(nx.all_pairs_dijkstra_path_length(copy_G, weight="weight"))
    rmc = pd.DataFrame.from_dict(rmc, orient="index")
    rmc_mean = rmc.mean()
    return rmc_mean


def prune_node_tree(main_T, u):
    """Prune a node from a tree graph
    
    Function that uses networkx grapgh method remove_node to prune a node.
    Also uses functionconnected_components to get the biggest subgraph

    Parameters
    ----------
    main_T : networkx.classes.graph.Graph
        A networkx Graph object of type tree
        with nodes and weighted arcs
    u : int
        Number of node that is desired to be
        pruned

    Returns
    -------

    
    """
    copy_T = main_T.copy()
    copy_T.remove_node(u)
    # Get the biggest subgraph of the connected_components
    copy_T = copy_T.subgraph(max(nx.connected_components(copy_T), key=len))
    return copy_T


def mst_pruning(main_T, threshold_N, buffer_area):
    """Prunes MST according to threesholds
    
    Function that prunes a tree graoh until one of the conditions of
    the thresholds is met.

    Parameters
    ----------
    main_T : networkx.classes.graph.Graph
        A networkx Graph object of type tree
        with nodes and weighted arcs
    threshold_N : float
        Percentage of N taht represents the minimum number of nodes
        that can have a tree

    Returns
    -------

    
    """
    copy_T = main_T.copy()
    N = copy_T.number_of_nodes()
    rmc_mean = all_rmc_mean(copy_T)
    hull_area = convex_hull(copy_T).area
    buffer_area = get_buffer_area(copy_T, buffer_area * rmc_mean.mean())
    flag = True
    while hull_area >= buffer_area and flag:

        # Get the node with maximum mean shortest paths
        # which emulates getting the fardest node
        u = rmc_mean.idxmax()
        copy_T = prune_node_tree(copy_T, u)
        n = copy_T.number_of_nodes()
        rmc_mean = all_rmc_mean(copy_T)
        hull_area = convex_hull(copy_T).area
        buffer_area = get_buffer_area(copy_T, 0.12 * rmc_mean.mean())

        if n <= threshold_N * N:
            flag = False
    return copy_T
