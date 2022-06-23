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
y_label = ['Precipitation [mm]', 'Temperature [' + degree_sign + 'C]', 'Temperature [' + degree_sign + 'C]']

fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
for name, ax, i in zip(['precip', 'tmin', 'tmax'], axes, range(3)):
       sns.boxplot(data=data.loc['1996':'2015'], x='month', y=name, ax=ax)
       ax.set_title(name)
       axes[i].set(ylabel=y_label[i])
# Remove the automatic x-axis label from all but the bottom subplot 
       if ax != axes[-1]:
              ax.set_xlabel('')

# %%
data.loc['2012', 'tmin'].plot()
# %%
