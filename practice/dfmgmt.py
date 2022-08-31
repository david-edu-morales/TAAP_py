# Create a function to generate separate dfs based on key id
def split_key_df(df, key):
    """Creates a separate dataframe from a master list based on key id.
    
    A master dataframe that contains a key id column can be separated into subset
    dfs based on the key id. This function is best utilized with a dictionary for
    loop outlined below:

    
    Parameters
    ----------
    df : df
        master dataframe from which to pull data
    key : int
        Key id for each climate station
        
    Returns
    ----------
    df[df['key'] == key]
    """

    return df[df['key'] == key]

# Create a function to generate separate dfs based on freq using a provided list of column names
cols = ['precip', 'evap', 'tmax', 'tmin']

def resample_mean(df, cols, freq):
    """Resamples data from a df utilizing a preset list of column names.
    
    Combining a list of column names, a dataframe, and a frequency code,
    this function resamples data according to the mean belonging to included 
    column names at the specified intervals.

    M = monthly; W = weekly; D = daily; Y = yearly

    Parameters
    ----------
    df : df
        dataframe that will have its data resampled
    cols : list
        list of column names that will have their data resampled
    freq : str
        Frequency code for establishing the interval of resampling

    Returns
    ---------- 
    df[cols].resample(str(freq)).mean()
    """

    return df[cols].resample(str(freq)).mean()