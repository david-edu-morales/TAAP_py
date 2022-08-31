# %%
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime as dt
from sklearn import linear_model
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys
varsSum_mx = ['precip']                                 # specifiy variables to be resampled
csvFile = 'climateStationTrends_Sum.csv'                # csv filename to collect linRegCoefs
headerList = ['key', 'variable', 'month', 'coef']       # header names for csv of linRegCoefs
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun',\
             'Jul','Aug','Sep','Oct','Nov','Dec']       # setup month names for graph
degree_sign = u'\N{DEGREE SIGN}'                        # degree sign code

# %%
# *** MEXICAN CLIMATE STATIONS ***
# Read the files into a df
# Create a dictionary of keys and filenames to call dataframes into another dictionary
filenameDict = {keylist_mx[key]: str(keylist_mx[key])+'_clean-data.csv' for key in range(len(keylist_mx))}

# Create a dictionary of keys and corresponding dataframes
dictCleanData = {key: pd.read_csv(filename,
                                  index_col = 'date',
                                  parse_dates=True)
                for (key, filename) in filenameDict.items()}

# %%
# Calculate rainfall for seasonal storm seasons for all stations
# Select precip data from QC'd database
dictPrecip = {key: dictCleanData[key][dictCleanData[key].variable == 'precip'] for key in keylist_mx}

# WINTER SEASON // WINTER SEASON // WINTER SEASON // WINTER SEASON // WINTER SEASON // WINTER SEASON
# Set up master dictionary to receive year & precipSum entries for all stations
dictWinPrecip = {}

for key in keylist_mx:
       df = dictPrecip[key]                             # simplify dataframe for reference
       stationData = {}                                 # dict to hold precipSum/yearList for single station
       yearList = df.index.year.unique().tolist()       # list to hold all available years
       precipSums = []                                  # list to hold precipSums for each year

       for year in yearList:
              # Create mask of desired dates for Winter rain-season
              mask = (df.index >= dt.datetime(year,11,1)) & (df.index <= dt.datetime(year+1,3,31))
              rainfall = df.loc[mask,['measurement']].sum()    # sum precip measurements from each day
              precipSums.append(rainfall[0])                   # add precipSum to list

       yearEntry = {'year' : yearList}           # create entry for list of years
       rainEntry = {'precipSum' : precipSums}    # create entry for list of precipSums
       stationData.update(yearEntry)             # add year entry to stationData dict
       stationData.update(rainEntry)             # add sums entry to stationData dict
       dictStation = {key:stationData}           # create entry of station key/data
       dictWinPrecip.update(dictStation)         # add stationData entry to winPrecip dict

dictWinPrecip = {key: pd.DataFrame.from_dict(dictWinPrecip[key]) for key in keylist_mx}

for key in keylist_mx:
       dictWinPrecip[key]['season'] = 'winter'
       dictWinPrecip[key]['year'] = pd.to_datetime(dictWinPrecip[key]['year'], format='%Y')
       dictWinPrecip[key] = dictWinPrecip[key].set_index('year')

# SUMMER SEASON // SUMMER SEASON // SUMMER SEASON // SUMMER SEASON // SUMMER SEASON // SUMMER SEASON
# Set up master dictionary to receive year & precipSum entries for all stations
dictSummPrecip = {}

for key in keylist_mx:
       df = dictPrecip[key]                             # simplify dataframe for reference
       stationData = {}                                 # dict to hold precipSum/yearList for single station
       yearList = df.index.year.unique().tolist()       # list to hold all available years
       precipSums = []                                  # list to hold precipSums for each year

       for year in yearList:
              # Create mask of desired dates for Summer rain-season
              mask = (df.index >= dt.datetime(year,6,1)) & (df.index <= dt.datetime(year,9,30))
              rainfall = df.loc[mask,['measurement']].sum()    # sum precip measurements from each day
              precipSums.append(rainfall[0])                   # add precipSum to list

       yearEntry = {'year' : yearList}           # create entry for list of years
       rainEntry = {'precipSum' : precipSums}    # create entry for list of precipSums
       stationData.update(yearEntry)             # add year entry to stationData dict
       stationData.update(rainEntry)             # add sums entry to stationData dict
       dictStation = {key:stationData}           # create entry of station key/data
       dictSummPrecip.update(dictStation)        # add stationData entry to summPrecip dict

dictSummPrecip = {key: pd.DataFrame.from_dict(dictSummPrecip[key]) for key in keylist_mx}

for key in keylist_mx:
       dictSummPrecip[key]['season'] = 'summer'
       dictSummPrecip[key]['year'] = pd.to_datetime(dictSummPrecip[key]['year'], format='%Y')
       dictSummPrecip[key] = dictSummPrecip[key].set_index('year')

# Combine seasonal dataframes
dictSeasonPrecip = {key: pd.concat([dictWinPrecip[key],dictSummPrecip[key]], sort=True) for key in keylist_mx}

# %%
