# %%
from tkinter import N
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from dfmgmt import *
import pandas as pd
from datetime import datetime
from sklearn import linear_model
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
# Create a dictionary of dfs utilizing a for loop and the split_key_df function
dfs = {key: split_key_df(data, key) for key in key_list}

# Create a function to generate separate dfs based on freq using a provided list of column names
cols = ['precip', 'evap', 'tmax', 'tmin']

# Create a dictionary of dfs utilizing a for loop and the resample_mean
dfs_m_mean = {key: resample_mean(dfs[key], cols, 'M') for key in key_list}

# %%

df = dfs_m_mean[26057][dfs_m_mean[26057].index.month == 12]

X = (df.index -  df.index[0]).days.reshape(-1, 1)
y = df['value'].values
linear_model.LinearRegression().fit(X, y)


# %%
degree_sign = u'\N{DEGREE SIGN}'

x = dfs_m_mean[26057][dfs_m_mean[26057].index.month == 12].index.year
y = dfs_m_mean[26057][dfs_m_mean[26057].index.month == 12]['tmax']

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel('Years')
ax.set_ylabel(degree_sign + 'C')
ax.set_title('Monthy Mean of Max Temperature\nClimate Station: 26057')

# %%
fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(11, 10), sharex=True)
for m, ax in zip(range(12), axes):
    x = dfs_m_mean[26057][dfs_m_mean[26057].index.month == m+1].index.year
    y = dfs_m_mean[26057][dfs_m_mean[26057].index.month == m+1]['tmax']
    axes.plot(x,y)

#%%
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig = plt.figure(figsize=(30,20))
fig.subplots_adjust(hspace=0.2, wspace=0.2)
for i in range(1,13):
       ax = fig.add_subplot(3,4,i)
       x = dfs_m_mean[26057][dfs_m_mean[26057].index.month == i].index.year
       y = dfs_m_mean[26057][dfs_m_mean[26057].index.month == i]['tmax']
       ax.plot(x,y)
       ax.set_ylabel(degree_sign+'C')
       ax.set_title(month_str[i-1], fontsize=15, fontweight='bold')

# %%
# Construct subplot figure to compare precip, tmin, and tmax along the same x-axis
y_label = ['Precipitation [mm]', 'Temperature [' + degree_sign + 'C]', 'Temperature [' + degree_sign + 'C]']

fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
for name, ax, i in zip(['precip', 'tmin', 'tmax'], axes, range(3)):
       sns.boxplot(data=data.loc['1996':'2015'], x='month', y=name, ax=ax)
       ax.set_title(name)
       axes[i].set(ylabel=y_label[i])
# Remove the automatic x-axis label from all but the bottom subplot 
       if ax != axes[-1]:
              ax.set_xlabel('')