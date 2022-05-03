"""
A module for validating coordinates in GIS
based on polygon generation
"""
import numpy as np
import pandas as pd
import networkx as nx
import shapely
import fiona
import geopandas as gpd
from sklearn.metrics.pairwise import euclidean_distances

from boundaries_algorithm.validation.np_module import (
    all_weight_arcs,
    node_attributes_generation,
)
from boundaries_algorithm.validation.pd_module import (
    sub_df_mask
)

from boundaries_algorithm.validation.nx_module import (
    mst,
    mst_pruning,
    all_rmc_mean,
    prune_node_tree,
)
from boundaries_algorithm.validation.poly_module import (
    convex_hull,
    identify_poly_inter,
    add_pts,
    filter_multipolygon
)

def dict_filter_multipoligon(main_loc_hull):
    """ Function that avoids having multipoligons in dictionary
    
    Parameters
    ----------
    main_loc_hull : dict with values as shapely.geometry.polygon.Polygon
        Dictionary with int keys as location and polygons as
        values

    Returns
    -------

    """
    copy_loc_hull = main_loc_hull.copy()
    new_loc_hull = {
        key: filter_multipolygon(value) for key, value in copy_loc_hull.items()
    }
    return new_loc_hull


def polygons_init(main_df, column_id, threshold_N, buffer_area, convert_1, convert_2):

    """Returns dictionaries of polygons and trees based
    on DataFrame and subset.
    
    Function that returns two dictionaries with keys as locations of the desired
    DataFrame column unique values in the specified subset. The values of the
    dictionaries are: (i) convex hulls as shapely.geometry.polygon.Polygon, and
    (ii) tree graph as networkx.classes.graph.Graph

    Parameters
    ----------
    main_df : pandas.core.frame.DataFrame
        DataFrame that contains all the information of nodes
        (i.e. coordinates)
    column : str
        column from the DataFrame that contains node locations
    threshold_N : float
        Percentage of N that represents the minimum number of nodes
        that can have a tree

    Returns
    -------

    
    """
    copy_df = main_df.copy()
    loc_hull = {}
    loc_tree = {}
    locs = copy_df[column_id].unique()
    for loc in locs:
        sub_df = sub_df_mask(
            copy_df, [convert_1, convert_2], copy_df[column_id] == loc
        )
        nodes = sub_df.index.values
        X = sub_df[convert_1].values
        Y = sub_df[convert_2].values
        arcs = all_weight_arcs(nodes, X, Y, euclidean_distances)
        node_attributes = node_attributes_generation(nodes, X, Y)
        T = mst(arcs, node_attributes)
        T = mst_pruning(T, threshold_N, buffer_area)
        # Save important information
        loc_tree[loc] = T
        loc_hull[loc] = convex_hull(T)
    return loc_hull, loc_tree


def poly_no_inter(main_loc_hull, main_loc_tree):
    """Eliminate intersections between polygons making them smaller
    
    Function that uses the prune_node_tree to iteratively prune nodes
    dor the biggest convex hull area until no intersections are
    detected

    Parameters
    ----------
    main_loc_hull : dict with values as shapely.geometry.polygon.Polygon
        Dictionary with int keys as location and polygons as
        values
    main_loc_tree : dict with values as networkx.classes.graph.Graph
        Dictionary with int keys as location and tree graphs as
        values
        

    Returns
    -------

    
    """
    copy_loc_hull = main_loc_hull.copy()
    copy_loc_tree = main_loc_tree.copy()
    poly_inter = identify_poly_inter(copy_loc_hull)
    # At the end all sets must have only one element
    flag = all(len(my_set) == 1 for my_set in poly_inter)
    while not flag:
        # Get biggest set
        my_set = max(poly_inter, key=len)
        # Extract from important dicts the info of set
        # Dont take trees with 3 nodes, because a tree with less nodes
        # will generate a convex hull as LineString
        sub_loc_hull_area = {
            key: copy_loc_hull[key].area
            for key in my_set
            if copy_loc_tree[key].number_of_nodes() > 3
        }
        sub_loc_tree = {
            key: copy_loc_tree[key]
            for key in my_set
            if copy_loc_tree[key].number_of_nodes() > 3
        }
        # Get the loc of my_set with biggest area
        loc = max(sub_loc_hull_area, key=sub_loc_hull_area.get)
        # Get the tree of the loc with biggest area
        T = sub_loc_tree[loc]
        # Prune tree
        rmc_mean = all_rmc_mean(T)
        u = rmc_mean.idxmax()
        T = prune_node_tree(T, u)
        # Update tree object in principal dict
        copy_loc_tree[loc] = T
        # Get convex hull
        hull = convex_hull(T)
        # Update convex hull object in principal dict
        copy_loc_hull[loc] = hull
        # Calculate intersections
        poly_inter = identify_poly_inter(copy_loc_hull)
        # Evaluate if all sets are of len 1
        flag = all(len(my_set) == 1 for my_set in poly_inter)
    return copy_loc_hull, copy_loc_tree


def smooth_polygons(main_loc_hull, N):
    """Generates thiessen polygons using interpolation of conex hulls

    Parameters
    ----------
    loc_hull : dict with values as shapely.geometry.polygon.Polygon
        Dictionary with int keys as location and polygons as
        values
    N : int
        Number of points desired to discretize the boundaries of a polygon
    main_loc_hull :
        

    Returns
    -------

    
    """
    copy_loc_hull = main_loc_hull.copy()
    # Get envelope fo thiessen polygons
    hull_pts = {key: add_pts(value, N) for key, value in copy_loc_hull.items()}
    pts = shapely.ops.unary_union(hull_pts.values())
    hull = pts.convex_hull
    loc_union_region = {}

    regions = shapely.ops.voronoi_diagram(pts)
    # Intersect regions with the hull envelope
    regions = {i: region.intersection(hull) for i, region in enumerate(regions.geoms)}
    # Look for intersection in regions
    gs = gpd.GeoSeries(regions)

    for key, value in hull_pts.items():
        inter_dict = {i: gs.intersects(pt) for i, pt in enumerate(value.geoms)}
        inter_df = pd.DataFrame(inter_dict).replace(False, np.nan)
        desired_regions = inter_df.dropna(how="all", axis=0).index.values
        # Make uniojn of the regions that were intersected
        union_region = shapely.ops.unary_union(
            [regions[region] for region in desired_regions]
        )
        loc_union_region[key] = union_region

    # Filter Multipolygon due to approximation
    copy_loc_hull = dict_filter_multipoligon(loc_union_region)

    # Intersecciones con convex hulls
    for key_1, value_1 in copy_loc_hull.items():
        for key_2, value_2 in main_loc_hull.items():
            if value_1.intersects(value_2):
                if key_1 == key_2:
                    copy_loc_hull[key_2] = value_2.union(value_1)
                else:
                    copy_loc_hull[key_2] = value_2.difference(value_1)

    return copy_loc_hull

def ident_good_proj(main_df, main_loc_hull, column_id, convert_1, convert_2):
    """Return an array with the id of projects inside the polygon thet
    specified
    
    This function uses geopandas GeoSeries to efficiently determine if points
    are within polygons

    Parameters
    ----------
    main_df : pandas.core.frame.DataFrame
        Dataframe that contains nodes as index and columns with
        coordinate information
    main_loc_hull : dict with values as shapely.geometry.polygon.Polygon
        Dictionary with int keys as location and polygons as
        values

    Returns
    -------

    
    """
    copy_df = main_df.copy()

    # GeoSerie for project points
    gdf = gpd.GeoDataFrame(
        copy_df[column_id],
        index=copy_df.index.values,
        geometry=gpd.points_from_xy(copy_df[convert_1].values, copy_df[convert_2].values),
    )
    # GeoSerie for polygons for good projects
    gs = gpd.GeoSeries(main_loc_hull)

    good_dict = {
        loc: gdf.intersects(gs[loc]) * (gdf[column_id] == loc) for loc in gs.index.values
    }
    good_df = pd.DataFrame(good_dict).replace(False, np.nan)
    good_df = good_df.dropna(how="all", axis=0)
    good_proy = good_df.index.values

    percentage = round(100 * good_proy.size / gdf.shape[0], 2)

    df_good = copy_df.loc[good_proy]
    set_good = set(good_proy)

    set_all = set(copy_df.index.values)
    set_bad = set_all.difference(set_good)
    bad_proy = list(set_bad)
    df_bad = copy_df.loc[bad_proy]

    return df_good, df_bad, percentage
