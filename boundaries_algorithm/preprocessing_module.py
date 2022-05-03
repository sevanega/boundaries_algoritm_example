"""
A module for data projections
"""
from pyproj import CRS, Transformer

def crs_transformer(crs_inical, crs_final):
    """Creates the transformer for epsg

    Parameters
    ----------
    crs_inical : str pyproj.crs.crs.CRS
        EPSG is a structured dataset of CRS and Coordinate Transformations. 
    crs_final : str pyproj.crs.crs.CRS
        EPSG is a structured dataset of CRS and Coordinate Transformations. 

    Returns
    -------
        
    
    """
    actual_CRS = CRS(crs_inical)
    convert_CRS = CRS(crs_final)
    transformer = Transformer.from_crs(actual_CRS, convert_CRS)
    return transformer


def crs_transformation(transformer, xi, yi):
    """Transforms coordines between different epsg

    Parameters
    ----------
    transformer : pyproj.transformer.Transformer
        Transformer between two coordinates systemas
    xi : numpy.ndarray
        array contaning node Y coordinates
    yi : numpy.ndarray
        array contaning node Y coordinates
        

    Returns
    -------

    
    """
    xf, yf = transformer.transform(xi, yi)
    return xf, yf


def coordinates_projection(main_df, actual_epsg, convert_epsg, actual_1, actual_2, convert_1, convert_2):
    """

    Parameters
    ----------
    main_df :  pandas.core.frame.DataFrame
        Dataframe that is going to be modified
    actual_epsg : str
        EPSG is a structured dataset of CRS and Coordinate Transformations. 
    convert_epsg : str
        EPSG is a structured dataset of CRS and Coordinate Transformations. 

    Returns
    -------

    
    """
    copy_df = main_df.copy()
    transformer = crs_transformer(actual_epsg, convert_epsg)
    copy_df[convert_1], copy_df[convert_2] = crs_transformation(
        transformer, copy_df[actual_1].values, copy_df[actual_2].values
    )
    return copy_df
