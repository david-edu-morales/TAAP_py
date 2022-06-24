# %%
from calendar import month
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

import os

# %%
# Read the files into a df and clean the data
# Create list of filenames
key_list = [26013, 26057, 26164]
filename_list = []

for k in range(len(key_list)):
       filename = str(key_list[k]) + '_daily-record.txt'
       filename_list.append(filename)

# Create a list of dfs
df_list = [pd.read_fwf(filename, skiprows=19, skipfooter=1,
                   names=['date',
                          'precip',
                          'evap',
                          'tmax',
                          'tmin'])
       for filename in filename_list]

# Add climate station key for each df
for k in range(len(key_list)):
       df_list[k]['key'] = key_list[k]

# Concatenate dfs
data = pd.concat(df_list)

# Swap strings to None type
data = data.replace({'Nulo': None}, regex=True)
data = data.replace({'ul' : None}, regex=True) # Necessary, but could not find anything using 
                                               # data.loc[data['evap'] == 'ul']

# Set dates to correct format
data['date'] = pd.to_datetime(data['date'],
                              infer_datetime_format=True,
                              dayfirst=True,
                              format='%Y-%m-%d')

# Set df index to the datetime
data = data.set_index('date')

# Assign float type to data and int type to key
data = data.astype(float)
data['key'] = data['key'].astype(int)

# Add month and year columns to df
data['year'] = data.index.year
data['month'] = data.index.month

# %%
# Create a function to 
def split_key_df(df, key):
    """Creates a separate dataframe from a master list based on key id.
    
    A master dataframe that contains a key id column can be separated into subset
    dfs based on the key id. This function is best utilized with a dictionary for
    loop outlined below:

    dfs = {key: split_key_df(data, key) for key in key_list}

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
    
    return df[df[str(key)] == key]

dfs = {key: split_key_df(data, key) for key in key_list}

# %%
# ***PRACTICE***
# Resample data
cols = ['precip', 'evap', 'tmax', 'tmin']

def resample_mean(df, cols, freq):
    return df[cols].resample(freq).mean()

dfs_m_resample = {key: resample_mean(dfs[key], cols, 'M') for key in key_list}

# %%
# Practice graph-splicing syntax
dfs_m_resample[26057].loc['2012']['tmax'].plot()

# %%
dfs_m_resample[26057]['month'] = dfs_m_resample[26057].index.month  

# %%
start, end = 2000, 2016

fig, axes = plt.subplots()
for year in range(start,end):
    dfs_m_resample[26057].loc[str(year)].plot(ax=axes, label=str(year), x='month', y='tmax')



# %%
fig, ax = plt.subplots()
ax.plot(data.loc[start:end, 'tmin'],
        marker='.',
        linestyle='-',
        linewidth=0.5,
        label='Daily')
ax.plot(data_wkly_mean.loc[start:end, 'tmin'],
        marker='o',
        markersize=5,
        linestyle='-',
        label='Weekly Mean Resample')
ax.set_ylabel('Temperature [' + degree_sign + 'C]')
ax.legend()