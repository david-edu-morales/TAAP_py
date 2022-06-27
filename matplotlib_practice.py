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

# Add month and year
dfs_m_mean[26057]['year']=dfs_m_mean[26057].index.year
dfs_m_mean[26057]['month']=dfs_m_mean[26057].index.month



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

       # Make the linear regression
       database= dfs_m_mean[26057].loc[dfs_m_mean[26057]['month']==i][['tmax','year']]
       database=database.dropna()

       x_data = database['year'].values.reshape(database.shape[0],1)
       y_data = database['tmax'].values.reshape(database.shape[0],1)

       reg = linear_model.LinearRegression().fit(x_data, y_data)
       coef = reg.coef_
       inter= reg.intercept_
       
       y_estimate = coef*x_data+inter

       ax.plot(x_data,y_estimate)
