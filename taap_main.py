# %%
from datetime import datetime
from dfmgmt import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})
from tkinter import N

import os

# %%
# *** MEXICAN CLIMATE STATIONS ***
# US data is analyzed @ line 140

# Read the files into a df and clean the data
# Create list of filenames
key_list_mx = [26013, 26057, 26164]
filename_list_mx = []

for k in range(len(key_list_mx)):
       filename = str(key_list_mx[k]) + '_daily-record.txt'
       filename_list_mx.append(filename)

# Create a list of dfs
df_list_mx = [pd.read_fwf(filename, skiprows=19, skipfooter=1,
                   names=['date',
                          'precip',
                          'evap',
                          'tmax',
                          'tmin'])
       for filename in filename_list_mx]

# Add climate station key for each df
for k in range(len(key_list_mx)):
       df_list_mx[k]['key'] = key_list_mx[k]

# Concatenate dfs
data_mx = pd.concat(df_list_mx)

# Swap strings to None type
data_mx = data_mx.replace({'Nulo': None}, regex=True)
data_mx = data_mx.replace({'ul' : None}, regex=True) # Necessary, but could not find anything using 
                                               # data.loc[data['evap'] == 'ul']

# Set dates to correct format
data_mx['date'] = pd.to_datetime(data_mx['date'],
                              infer_datetime_format=True,
                              dayfirst=True,
                              format='%Y-%m-%d')

# Set df index to the datetime
data_mx = data_mx.set_index('date')

# Assign float type to data and int type to key
data_mx = data_mx.astype(float)
data_mx['key'] = data_mx['key'].astype(int)

# Add month and year columns to df
data_mx['year'] = data_mx.index.year
data_mx['month'] = data_mx.index.month

# %%
# Create a dictionary of dfs utilizing a for loop and the split_key_df function
dfs_mx = {key: split_key_df(data_mx, key) for key in key_list_mx}

# Create a function to generate separate dfs based on freq using a provided list of column names
cols_mx = ['precip', 'evap', 'tmax', 'tmin']

# Create a dictionary of dfs utilizing a for loop and the resample_mean
dfs_mm_mx = {key: resample_mean(dfs_mx[key], cols_mx, 'M') for key in key_list_mx}

# Add month and year
dfs_mm_mx[26057]['year']=dfs_mm_mx[26057].index.year
dfs_mm_mx[26057]['month']=dfs_mm_mx[26057].index.month

# %%
# Automate 12-plot monthly mean plot for variables
# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
df_mm_mx_last40 = dfs_mm_mx[26057].loc[str(start):str(end)]
degree_sign = u'\N{DEGREE SIGN}'

for col in cols_mx:
       fig = plt.figure(figsize=(24,16))
       fig.subplots_adjust(hspace=0.2, wspace=0.2)
       fig.suptitle("Monthly Mean for "+col+"\nClimate Station 26057", fontsize=30)
       
       for i in range(1,13):
              ax = fig.add_subplot(3,4,i)
              x = df_mm_mx_last40[df_mm_mx_last40.index.month == i].index.year
              y = df_mm_mx_last40[df_mm_mx_last40.index.month == i][col]

              ax.plot(x,y) # this plots the col values

              # Col-alike subplot formatting              
              ax.set_title(month_str[i-1], fontsize=20, fontweight='bold')

              # Make the linear regression
              database= df_mm_mx_last40.loc[df_mm_mx_last40['month']==i][[col,'year']]
              database=database.dropna()

              x_data = database['year'].values.reshape(database.shape[0],1)
              y_data = database[col].values.reshape(database.shape[0],1)

              reg = linear_model.LinearRegression().fit(x_data, y_data)
              coef = reg.coef_
              inter= reg.intercept_
              y_estimate = coef*x_data+inter # y=mx+b, possible option to upgrade

              ax.plot(x_data,y_estimate) # this plots the linear regression

              # Col-dependent subplot formatting
              if col == cols_mx[0]:
                     ax.set_ylabel('mm')
                     ax.text(.1, .8,
                             str(round((end-start)*coef[0,0],2))+'mm/40yr',
                             transform=ax.transAxes,
                             fontsize=24,
                             color='red')
              elif col == cols_mx[1]: # cannot figure out how to combine cols_mx[0:2]
                     ax.set_ylabel('mm')
                     ax.text(.1, .8,
                             str(round((end-start)*coef[0,0],2))+'mm/40yr',
                             transform=ax.transAxes,
                             fontsize=24,
                             color='red')
              else:
                     ax.set_ylabel(degree_sign+'C')
                     ax.text(.1, .8,
                             str(round((end-start)*coef[0,0],2))+degree_sign+'C/40yr',
                             transform=ax.transAxes,
                             fontsize=24,
                             color='red')

       plt.savefig('26057_'+col+'-mm')

# %%
# *** US CLIMATE STATIONS ***

# Read the files into a df and clean the data
# Create list of filenames
key_list_us = [22139, 22140]
filename_list_us = []

for k in range(len(key_list_us)):
       filename = str(key_list_us[k]) + '_daily-record.txt'
       filename_list_us.append(filename)

# Create a list of dfs
df_list_us = [pd.read_fwf(filename, skiprows=2,
                       names=['station',
                              'date',
                              'precip',
                              'tmax',
                              'tmin'])
       for filename in filename_list_us]

# Add climate station key for each df
for k in range(len(key_list_us)):
       df_list_us[k]['key'] = key_list_us[k]

# Concatenate dfs
data_us = pd.concat(df_list_us)
data_us = data_us[['date','precip','tmax','tmin','key']]

# Swap non-records to None type
data_us = data_us.replace({-999.0: None, -9999.0: None}, regex=True)

# Set dates to correct format
data_us['date'] = pd.to_datetime(data_us['date'], format='%Y%m%d').dt.strftime("%Y-%m-%d")
data_us['date'] = pd.to_datetime(data_us['date'], format='%Y-%m-%d')

# Set df index to the datetime
data_us = data_us.set_index('date')

# Add month and year columns to df
data_us['year'] = data_us.index.year
data_us['month'] = data_us. index.month

# %%
# Create a dictionary of dfs utilizing a for loop and the split_key_df function
dfs_us = {key: split_key_df(data_us, key) for key in key_list_us}

# Create a function to generate separate dfs based on freq using a provided list of column names
cols_us = ['precip', 'tmax', 'tmin']

# Create a dictionary of dfs utilizing a for loop and the resample_mean
dfs_mm_us = {key: resample_mean(dfs_us[key], cols_us, 'M') for key in key_list_us} # mm = monthly mean

# Add month and year to each df in dict
for key in key_list_us:
       dfs_mm_us[key]['month'] = dfs_mm_us[key].index.month
       dfs_mm_us[key]['year'] = dfs_mm_us[key].index.year

# %%
# Automate 12-plot monthly mean plot for variables
# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
df_mm_us_last40 = dfs_mm_us[22140].loc[str(start):str(end)]
degree_sign = u'\N{DEGREE SIGN}'

for col in cols_us:
       fig = plt.figure(figsize=(24,16))
       fig.subplots_adjust(hspace=0.2, wspace=0.2)
       fig.suptitle("Monthly Mean for "+col+"\nClimate Station 22140", fontsize=30)
       
       for i in range(1,13):
              ax = fig.add_subplot(3,4,i)
              x = df_mm_us_last40[df_mm_us_last40.index.month == i].index.year
              y = df_mm_us_last40[df_mm_us_last40.index.month == i][col]

              ax.plot(x,y) # this plots the col values

              # Col-alike subplot formatting              
              ax.set_title(month_str[i-1], fontsize=20, fontweight='bold')

              # Make the linear regression
              database= df_mm_us_last40.loc[df_mm_us_last40['month']==i][[col,'year']]
              database=database.dropna()

              x_data = database['year'].values.reshape(database.shape[0],1)
              y_data = database[col].values.reshape(database.shape[0],1)

              reg = linear_model.LinearRegression().fit(x_data, y_data)
              coef = reg.coef_
              inter= reg.intercept_
              y_estimate = coef*x_data+inter # y=mx+b, possible option to upgrade

              ax.plot(x_data,y_estimate) # this plots the linear regression

              # Col-dependent subplot formatting
              if col == cols_us[0]:
                     ax.set_ylabel('mm')
                     ax.text(.1, .8,
                             str(round((end-start)*coef[0,0],2))+'mm/40yr',
                             transform=ax.transAxes,
                             fontsize=24,
                             color='red')
              else:
                     ax.set_ylabel(degree_sign+'C')
                     ax.text(.1, .8,
                             str(round((end-start)*coef[0,0],2))+degree_sign+'C/40yr',
                             transform=ax.transAxes,
                             fontsize=24,
                             color='red')

       plt.savefig('22140_'+col+'-mm')