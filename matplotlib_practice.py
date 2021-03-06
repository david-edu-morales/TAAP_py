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
# Multiply mean by # of days for "cumulative" monthly values
# Remember to consider leap year, perhaps create two lists 
# 1) "normal" day distro and 2) leap-yr distro. Every four years calls list 2
# Leap-years: 2020, 2016, 2012, 2008, ...

day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] # "normal" year distro
ly_list = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] # leap-year distro

for i in range(12):
       dfs_mm_mx[26057]['precip_cum'] = dfs_mm_mx[26057][dfs_mm_mx[26057]['month'] == i+1][['precip']] * day_list[i]
       
# %%
for i in range(2):
       dfs_mm_mx[26057]['precip_cum'] = dfs_mm_mx[26057][dfs_mm_mx[26057]['month'] == i+1][['precip']].multiply(day_list[i])

# %%
test = pd.DataFrame({
              "A" : [1,2,3,4,5],
              "B" : [2,4,6,8,10]
       })
# %%
dict_cmm_mx = {month: dfs_mm_mx[26057][dfs_mm_mx[26057]['month'] == month+1][['precip']] * day_list[month] for month in range(12)}
df_cmm_26057 = pd.concat(dict_cmm_mx.values(), axis=0)
df_cmm_26057 = df_cmm_26057.sort_index()
df_cmm_26057 = df_cmm_26057.rename(columns={'precip':'precip_cum'})
# Create a dictionary of dfs utilizing a for loop and the resample_mean
# dfs_mm_mx = {key: resample_mean(dfs_mx[key], cols_mx, 'M') for key in key_list_mx}

# %%
# Brief stat analysis
for m in range(1,13):
       print(df_cmm_26057[df_cmm_26057.index.month == m].std())
# %%
