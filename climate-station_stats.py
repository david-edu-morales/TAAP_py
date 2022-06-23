# %%
# Step 1 - Download the data from the CONAGUA website
# https: // smn.conagua.gob.mx/es/climatologia/informacion-climatologica/
#           informacion-estadistica-climatologica
# Units:
#       datetime: dd/mm/yyyy
#       precip: mm
#       evap: mm
#       tmax/tmin: Celsius

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

import os

# %% 
# Read in the file in as df and clean the data
key_id = 26057
filename = str(key_id) + '_daily-record.txt'
filepath = os.path.join('metadata/' + str(key_id), filename)

# Correct space-delimited columns from .txt files
data = pd.read_fwf(filename, skiprows=19, skipfooter=1,
                   names=['date',
                          'precip',
                          'evap',
                          'tmax',
                          'tmin'])

# Swap strings to None type
data = data.replace({'Nulo': None}, regex=True)
data = data.replace({'ul' : None}, regex=True)

# Set dates to correct format
data['date'] = pd.to_datetime(data['date'],
                              infer_datetime_format=True,
                              dayfirst=True,
                              format='%Y-%m-%d')

# Set df index to the datetime
data = data.set_index('date')

# Assign float type to data
data = data.astype(float)

# Add month and year columns to df
data['year'] = data.index.year
data['month'] = data. index.month

# %%
# Make a plot of the data
degree_sign = u'\N{DEGREE SIGN}'

ax = data.loc['2008']['tmin'].plot(linewidth=0.5)
ax.set_ylabel('Temperature [' + degree_sign + 'C]')
ax.set_xlabel('Date')

# %%
# Tutorial from dataquest.io 'timeseries analysis with pandas dataframes'
cols_plot = ['precip', 'tmin', 'tmax']
axes = data.loc['1996':'2015'][cols_plot].plot(marker='.',
                                               alpha=0.5,
                                               linestyle='None',
                                               figsize=(11, 9),
                                               subplots=True)
for ax in axes:
    ax.set_ylabel('Daily Totals (GWh)')

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

fig.suptitle("Climate Station " + str(key_id), fontsize=25)

# %%
data.loc['2012', 'tmin'].plot()

# %%
# Resample data into 7-day (weekly) means
data_cols = ['precip', 'evap', 'tmin', 'tmax']

data_wkly_mean = data[data_cols].resample('W').mean()
data_wkly_mean.head()
data_wkly_mean.loc['2012', 'tmin'].plot()

# %%
# Constructing combination plot with daily and weekly resampled data
# Tutorial from dataquest.io 'timeseries analysis with pandas dataframes'
start, end = '2000-01', '2012-12'

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

# %%
# Find monthly sums of precip data
precip_monthly = data[['precip']].resample('M').sum(min_count=28)
precip_monthly.head(3)

fig, ax = plt.subplots()
ax.plot(precip_monthly.loc[start:end, 'precip'], color='black', label='precipitation')
ax.legend()
ax.set_ylabel('Precipitation [mm]')
# %%
