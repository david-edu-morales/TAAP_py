# %%
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime as dt
from sklearn import linear_model
import csv
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys
varsSum_mx = ['precip']                                 # specify variables to be resampled
seasons = ['summer', 'winter']                          # specify seasons to be graphed
csvFile = 'data/historicalTrends_precipSum.csv'     # csv filename to collect linRegCoefs
headerList = ['key', 'season', 'coef']       # header names for csv of linRegCoefs

# %%
# *** MEXICAN CLIMATE STATIONS ***
# Read the files into a df
# Create a dictionary of keys and filenames to call dataframes into another dictionary
filenameDict = {keylist_mx[key]: 'data/'+str(keylist_mx[key])+'_clean-data.csv' for key in range(len(keylist_mx))}

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
       dictWinPrecip[key].drop(dictWinPrecip[key].tail(1).index,inplace=True)

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
       dictSummPrecip[key].drop(dictSummPrecip[key].tail(1).index,inplace=True)

# Combine seasonal dataframes
dictSeasonPrecip = {key: pd.concat([dictWinPrecip[key],dictSummPrecip[key]], sort=True) for key in keylist_mx}

# %%
# Create precipSum csv files for MCA
for key in keylist_mx:
       dictSeasonPrecip[key].to_csv('data/'+str(key)+'_seasonalSum.csv')
# %%
# Re-create the 12-month plots for each station/variable using the quality-controlled data

with open(csvFile, 'w') as file:       # set mode to write w/ truncation
       dw = csv.DictWriter(file, delimiter=',',
                           fieldnames=headerList)
       dw.writeheader()

# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years

for key in keylist_mx:
       df = dictSeasonPrecip[key]       # rename working database for ease of reading      

       for var in varsSum_mx:

              fig = plt.figure(figsize=(21,7))
              fig.subplots_adjust(hspace=0.2, wspace=0.2)

              # Var-dependent figure title
              fig.suptitle("Total Rainfall by Season"+"\nClimate Station "+str(key), fontsize=22)
              
              for i in range(len(seasons)):
                     ax = fig.add_subplot(1,2, i+1)    # creates a 12-plot fig (3r x 4c)

                     # select data to plot
                     x = df[df.season == seasons[i]].tail(40).index.year
                     y = df[df.season == seasons[i]].precipSum.tail(40)

                     ax.plot(x,y)  # this plots the col values

                     # Var-alike subplot formatting              
                     ax.set_title(seasons[i], fontsize=24, fontweight='bold')

                     # Make the linear regression
                     database = df[(df.season == seasons[i])][[]].tail(40)
                     database = database.dropna()

                     # Reshape data for use in LinReg builder
                     x_data = x.values.reshape(x.shape[0],1)
                     y_data = y.values.reshape(y.shape[0],1)

                     reg = linear_model.LinearRegression().fit(x_data, y_data)
                     coef = reg.coef_
                     inter= reg.intercept_
                     y_estimate = coef*x_data+inter # y=mx+b, possible option to upgrade

                     ax.plot(x_data,y_estimate) # this plots the linear regression
                     
                     # Save the observed trends to a csv to be plotted on monte carlo distribution
                     saveLine = '\n'+str(key)+','+seasons[i]+','+str(40*coef[0,0])

                     saveFile = open(csvFile, 'a')   # reopen csv file
                     saveFile.write(saveLine)        # append the saved row
                     saveFile.close()
                     
                     # Var-dependent subplot formatting
                     ax.set_ylabel('mm', fontsize=18)
                     ax.tick_params(axis='both', which='major', labelsize=18)
                     ax.text(.1, .8,
                            str(round((end-start)*coef[0,0],2))+'mm/40yr',
                            transform=ax.transAxes,
                            fontsize=24,
                            color='red')
                     
                     plt.savefig('graphs/sumPlots/'+str(key)+'_precip-seasonal_sum')
                     

# %%
