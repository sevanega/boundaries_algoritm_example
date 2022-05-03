"""
A module for procesing shapely Polygons
"""
import numpy as np
import pandas as pd
import networkx as nx
import shapely
import fiona
import geopandas as gpd

from boundaries_algorithm.validation.set_module import set_integration


def convex_hull(main_T):
    """Returns the convex hull as shapely polygon
    
    Funtion that uses a DataFrame and a tree graph nodes to return a
    convex hull polygon that contains all the tree nodes

    Parameters
    ----------
    main_T : networkx.classes.graph.Graph
        A networkx Graph object of type tree
        with nodes and weighted arcs

    Returns
    -------

    
    """
    copy_T = main_T.copy()
    node_attributes = nx.get_node_attributes(copy_T, "xy")
    # Create an array of points containing X and Y
    # coordinates of nodes
    pts = np.array([*node_attributes.values()])
    pts = shapely.geometry.MultiPoint(pts)
    hull = pts.convex_hull
    return hull


def get_buffer_area(main_T, radius):
    """Given a MST returns the obtained buffer area with desired radius
    of the set of nodes in the graph

    Parameters
    ----------
    main_T : networkx.classes.graph.Graph
        A networkx Graph object of type tree
        with nodes and weighted arcs
    radius : float
        Value of teh desired radius of buffers

    Returns
    -------

    
    """
    copy_T = main_T.copy()
    node_attributes = nx.get_node_attributes(copy_T, "xy")
    x, y = zip(*node_attributes.values())

    buffer = make_buffer(node_attributes.keys(), x, y, radius)
    area = buffer.area

    return area


def make_buffer(nodes, X, Y, radius):
    """Returns a union of buffer of certain radius given
    nodes and coordinates

    Parameters
    ----------
    nodes : numpy.ndarray
        array contaning node numbers
    X : numpy.ndarray
        array contaning node X coordinates
    Y : numpy.ndarray
        array contaning node Y coordinates
    radius : float
        Value of teh desired radius of buffers

    Returns
    -------

    
    """
    gs = gpd.GeoSeries(gpd.points_from_xy(X, Y), index=nodes)
    buffer = gs.buffer(radius).unary_union
    return buffer


def identify_poly_inter(main_loc_hull):
    """Return a list of sets with the keys of the polygons that intersect
    each other

    Parameters
    ----------
    main_loc_hull : dict with values as shapely.geometry.polygon.Polygon
        Dictionary with int keys as location and polygons as
        values
        

    Returns
    -------

    
    """

    copy_loc_hull = main_loc_hull.copy()
    gs = gpd.GeoSeries(copy_loc_hull)
    inter_dict = {loc: gs.intersects(copy_loc_hull[loc]) for loc in gs.index.values}
    inter_df = pd.DataFrame(inter_dict).replace(False, np.nan)
    set_list = [set(inter_df[col].dropna().index.values) for col in inter_df]
    set_list = set_integration(set_list)
    return set_list


def add_pts(polygon, N):
    """Creates N additional random points over boundaries of polygon

    Parameters
    ----------
    polygon : shapely.geometry.polygon.Polygon
        Desired polygon to be discretized
    N : int
        Number of points desired to discretize the boundaries of a polygon

    Returns
    -------

    
    """
    pts = shapely.geometry.MultiPoint(
        [
            polygon.exterior.interpolate(i, normalized=True)
            for i in np.linspace(0, 1, N + 1)
        ]
        + list(polygon.exterior.coords)
    )
    return pts

def filter_multipolygon(polygon):
    """If polygon returns the same polygon, if multipolygon returns the
    biggest polygon in the geometry collection

    Parameters
    ----------
    polygon : shapely.geometry.Multipolygon or shapely.geometry.Polygon
        

    Returns
    -------

    
    """
    if type(polygon) == shapely.geometry.multipolygon.MultiPolygon:
        new_polygon = max(polygon, key=lambda x: x.area)
    elif type(polygon) == shapely.geometry.polygon.Polygon:
        new_polygon = polygon
    else:
        new_polygon = None
    return new_polygon
