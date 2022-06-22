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
import matplotlib.pyplot as plt
from datetime import datetime
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

# Swap 'Nulo' value to None type
data = data.replace({'Nulo': None}, regex=True)
data = data.replace({'ul' : None}, regex=True)

# Set dates to correct format
data['date'] = pd.to_datetime(data['date'], infer_datetime_format=True, format='%Y-%m-%d')

# Set df index to the datetime
data = data.set_index('date')

# Assign float type to data
data = data.astype(float)

# %%
# Make a plot of the data
degree_sign = u'\N{DEGREE SIGN}'

ax=data['tmax'].plot(linewidth=0.5)
ax.set_ylabel('Temperature [' + degree_sign + 'C]')
ax.set_xlabel('Date')

# %%
