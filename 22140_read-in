# %%
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

import os

# %%
# Read the files into a df and clean the data
# Create list of filenames
key_list = [22139, 22140]
filename_list = []

for k in range(len(key_list)):
       filename = str(key_list[k]) + '_daily-record.txt'
       filename_list.append(filename)

# Create a list of dfs
df_list = [pd.read_fwf(filename, skiprows=2,
                       names=['station',
                              'date',
                              'precip',
                              'tmax',
                              'tmin'])
       for filename in filename_list]

# Add climate station key for each df
for k in range(len(key_list)):
       df_list[k]['key'] = key_list[k]

# Concatenate dfs
data = pd.concat(df_list)
data = data[['date','precip','tmax','tmin','key']]

# Swap strings to None type
data = data.replace({-9999: None}, regex=True)

# Set dates to correct format
data['date'] = pd.to_datetime(data['date'], format='%Y%m%d').dt.strftime("%Y-%m-%d")
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
# Set df index to the datetime
data = data.set_index('date')

# Add month and year columns to df
data['year'] = data.index.year
data['month'] = data. index.month

# %%
