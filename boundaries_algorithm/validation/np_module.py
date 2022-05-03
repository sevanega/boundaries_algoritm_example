"""
A module for processing numpy arrays
"""
import numpy as np

def calculate_distances(x, y, function):
    """Calculates distances between all points according to function
    
    The function uses triangular matrix properties to be consistent with
    all_weight_arcs function

    Parameters
    ----------
    x : numpy.ndarray
        array contaning node X coordinates
    y : numpy.ndarray
        array contaning node Y coordinates
    function : funtion
        function from sklearn.metrics.pairwaise package
        to calculate distances between arrays

    Returns
    -------

    
    """
    x_y = np.column_stack((x, y))
    dist_matrix = np.triu(function(x_y))
    dist_matrix[np.tril_indices(dist_matrix.shape[0], 0)] = np.nan
    # Transforming the matrix of size (x.size, y.size) into a array
    # with only the relevant information of all possible combinations
    distances = dist_matrix[(~np.isnan(dist_matrix))]
    return distances


def all_weight_arcs(nodes, X, Y, function):
    """Returns all the weighted arcs needed for a complete graph
    
    The function uses triangular matrix properties to
    make the process more efficient when matching arcs
    with corresponding weights (e.i. distances)

    Parameters
    ----------
    nodes : numpy.ndarray
        array containing node numbers
    X : numpy.ndarray
        array contaning node X coordinates
    Y : numpy.ndarray
        array contaning node Y coordinates
    function : function
        function from sklearn.metrics.pairwaise package
        to calculate distances between arrays

    Returns
    -------

    
    """
    size = nodes.size
    # Creates a meshgrid a reshape it to obtain
    # all possible permutations between nodes
    all_arcs = np.array(np.meshgrid(nodes, nodes)).T.reshape(-1, 2)
    # Mask the permutations to get only the possible combinations
    ones = np.ones((size, size))
    triu_ones = np.triu(ones, 1)
    mask = np.array(triu_ones.flatten(), dtype=bool)
    all_arcs = all_arcs[mask]
    i, j = np.hsplit(all_arcs, 2)
    weights = calculate_distances(X, Y, function)
    # Create the tuples of (u, v, w)
    nec_arcs = np.vstack((i.reshape(-1), j.reshape(-1), weights))
    return nec_arcs.T


def node_attributes_generation(nodes, X, Y):
    """Returns cooridnates as node_atributes

    Parameters
    ----------
    nodes : numpy.ndarray
        array containing node numbers
    X : numpy.ndarray
        array contaning node X coordinates
    Y : numpy.ndarray
        

    Returns
    -------

    
    """
    node_attributes = {node: (X[i], Y[i]) for i, node in enumerate(nodes)}
    return node_attributes
