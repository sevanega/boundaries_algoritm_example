"""
A module for processing pandas DataFrames
"""
import pandas as pd

def sub_df_mask(main_df, columns, mask):
    """Creates a sub_df with a mask and specific columns
    
    The function extracts specific columns of a main_df
    using a desired mask

    Parameters
    ----------
    main_df : pandas.core.frame.DataFrame
        DataFrame that is going to be subset
    columns : list of str
        Column names of the Dataframe that are
        going to be extracted
    mask : pandas.core.frame.DataFrame
        Desired DataFrame mask of the type
        df['column'] == value

    Returns
    -------

    
    """
    copy_df = main_df.copy()
    sub_df = pd.DataFrame(
        {column: copy_df.loc[mask, column].values for column in columns},
        index=copy_df.loc[mask].index.values,
    )
    return sub_df
