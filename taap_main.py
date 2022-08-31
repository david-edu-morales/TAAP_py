# %%
from ast import Dict
import datetime as dt
from dfmgmt import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
from random import randint
from sklearn import linear_model
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})
from tkinter import N

import os

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys
vars_mx = ['precip', 'evap', 'tmax', 'tmin']            # specifiy variables to be resampled
csvFile = 'climateStationTrends_taap.csv'               # csv filename to collect linRegCoefs
headerList = ['key', 'variable', 'month', 'coef']       # header names for csv of linRegCoefs
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun',\
             'Jul','Aug','Sep','Oct','Nov','Dec']       # setup month names for graph
degree_sign = u'\N{DEGREE SIGN}'                        # degree sign code


# %%
# *** MEXICAN CLIMATE STATIONS ***
# US data is analyzed @ line 140
# Read the files into a df and clean the data
# Create a dictionary of keys and filenames to call dataframes into another dictionary
filenameDict = {keylist_mx[key]: str(keylist_mx[key])+'_daily-record.txt' for key in range(len(keylist_mx))}

# Create a dictionary of keys and corresponding dataframes
dict_mx = {key: pd.read_fwf(filename,
                            skiprows=19,
                            skipfooter=1,
                            names=['date',
                                   'precip',
                                   'evap',
                                   'tmax',
                                   'tmin'])
              for (key, filename) in filenameDict.items()}

# Edit data and prep for analysis 
for key in keylist_mx:
       dict_mx[key] = dict_mx[key].replace({'Nulo': None}, regex=True)       # swap str to None type
       dict_mx[key] = dict_mx[key].replace({'ul' : None}, regex=True)
       dict_mx[key]['date'] = pd.to_datetime(dict_mx[key]['date'],           # correct date format
                                             infer_datetime_format=True,
                                             dayfirst=True,
                                             format='%Y-%m-%d')
       dict_mx[key] = dict_mx[key].set_index('date')                         # set to datetimeIndex
       dict_mx[key] = dict_mx[key].astype(float)                             # correct datatypes

# %%
# Melt the dataframe to arrange one observation per row
dictMelt = {key: pd.melt(frame=dict_mx[key],
                         value_vars=['precip','evap','tmax','tmin'],
                         value_name='measurement',
                         var_name='variable',
                         ignore_index=False)
                     for key in keylist_mx}

# Identify leap years contained within the data
leapYear = [1932, 1936, 1940, 1944, 1952, 1956, 1960, 1972, 1976,
            1980, 1984, 1988, 1992, 2000, 2004, 2008, 2012, 2016]
# dictMelt[26057][(dictMelt[26057].index.day == 29) &
                           #(dictMelt[26057].month == 2)].index.year.unique().tolist()

# Create function that inputs the number of days in a month to be applied across rows
def days_of_month(row):
       x = row['month']
       if (row['year'] in leapYear):
              dayList = [31,29,31,30,31,30,31,31,30,31,30,31]
       else:
              dayList = [31,28,31,30,31,30,31,31,30,31,30,31]
       return dayList[x-1]

# Count the number of Nan values for each month.
for key in keylist_mx:
       df = dictMelt[key]                 # Temporary rename of iterated df
       df['month'] = df.index.month       # Add month column
       df['year'] = df.index.year         # Add year column
       # Count the total number of null values by month/year/variable (for <= 10 values rule)
       df['null_count'] = df.measurement.isnull().groupby([df['variable'],
                                                           df['month'],
                                                           df['year']]).transform('sum').astype(int)
       # Count the number of valid observations by month/year/variable (for <= 10 values rule)
       #      Some months may have only 15 (for ex.) valid records with no null values. 
       #      This would escape above filter.
       df['days_of_record'] = df.month.notnull().groupby([df['variable'],
                                                          df['month'],
                                                          df['year']]).transform('sum').astype(int)
       # Add the number of days for each month, sensitive to leap years.
       df['days_of_month'] = df.apply(lambda row: days_of_month(row), axis=1)
       #      
       df['min_days_reqd'] = df.days_of_month - 10
       cons_null = df.measurement.isnull().astype(int).groupby(df.measurement.notnull().astype(int).cumsum()).transform('sum')
       df['cons_null'] = cons_null
       df['cons_null_max'] = df.cons_null.groupby([df['variable'],
                                                 df['month'],
                                                 df['year']]).transform('max')

# Remove months w/ > 10 missing values 
dictMelt = {key: dictMelt[key][dictMelt[key]['null_count'] <= 10] for key in keylist_mx}

# Remove months w/ fewer days of record than required minimum
dictMelt = {key: dictMelt[key][dictMelt[key].days_of_record + dictMelt[key].null_count > 
                 dictMelt[key].min_days_reqd] for key in keylist_mx}

# Remove months w/ > 5 consecutive missing values
dictMelt = {key: dictMelt[key][dictMelt[key].cons_null_max <= 5] for key in keylist_mx}

# Remove unneeded columns
dictMelt = {key: dictMelt[key][['variable','measurement','month','year']] for key in keylist_mx}

# %%
# Determine the monthly averages (Tn, Tx, and ET) and sums (precip) from the climatological data
dictMonthly = {}     # create dictionary to receive for loop outputs

for key in keylist_mx:
       # First, calculate monthly averages
       grouped = dictMelt[key].groupby('variable')                    # group data by variable
       monthlyAvg = grouped.resample('M')[['measurement']].mean()     # calc monthly mean of all variables
       monthlyAvg = monthlyAvg.loc[['evap', 'tmax', 'tmin']]          # drop the resampled precip data
       monthlyAvg = monthlyAvg.reset_index(level='variable')          # return multiindex to 'variable' column

       # Second, calculate monthly sums for precip
       monthlySum = grouped.get_group('precip').resample('M')[['measurement']].sum()
       monthlySum['variable'] = 'precip'                              # return 'variable' column
       monthlySum = monthlySum[['variable','measurement']]            # re-order columns

       # Third, join data and reset 'month' and 'year' columns
       monthlyData = pd.concat([monthlyAvg, monthlySum])              # combine calc'd avgs and sums
       monthlyData['month'] = monthlyData.index.month
       monthlyData['year'] = monthlyData.index.year

       # Fourth, create element to append to dictionary
       data = {key: monthlyData}                                      # temporary element for update
       dictMonthly.update(data)                                       # append element to dictionary

# %%
# Re-create the 12-month plots for each station/variable using the quality-controlled data
'''
with open(csvFile, 'w') as file:       # set mode to write w/ truncation
       dw = csv.DictWriter(file, delimiter=',',
                           fieldnames=headerList)
       dw.writeheader()
'''
# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years

for key in keylist_mx:
       df = dictMonthly[key]       # rename working database for ease of reading      

       for var in vars_mx:

              fig = plt.figure(figsize=(24,16))
              fig.subplots_adjust(hspace=0.2, wspace=0.2)

              # Var-dependent figure title
              if var == vars_mx[0]:
                     fig.suptitle("Monthly Sum for "+var+"\nClimate Station "+str(key), fontsize=30)
              else:
                     fig.suptitle("Monthly Mean for "+var+"\nClimate Station "+str(key), fontsize=30)
              
              for month in range(1,13):
                     ax = fig.add_subplot(3,4,month)    # creates a 12-plot fig (3r x 4c)

                     # select data to plot
                     x = df[(df.index.month == month) & (df.variable == var)].tail(40).index.year
                     y = df[(df.index.month == month) & (df.variable == var)].measurement.tail(40)

                     ax.plot(x,y)  # this plots the col values

                     # Var-alike subplot formatting              
                     ax.set_title(month_str[month-1], fontsize=20, fontweight='bold')

                     # Make the linear regression
                     database = df[(df.index.month==month) & (df.variable==var)][['measurement','year']].tail(40)
                     database = database.dropna()

                     # Reshape data for use in LinReg builder
                     x_data = database['year'].values.reshape(database.shape[0],1)
                     y_data = database['measurement'].values.reshape(database.shape[0],1)

                     reg = linear_model.LinearRegression().fit(x_data, y_data)
                     coef = reg.coef_
                     inter= reg.intercept_
                     y_estimate = coef*x_data+inter # y=mx+b, possible option to upgrade

                     ax.plot(x_data,y_estimate) # this plots the linear regression
                     '''
                     # Save the observed trends to a csv to be plotted on monte carlo distribution
                     saveLine = '\n'+str(key)+','+str(var)+','+str(month)+','+str(40*coef[0,0])

                     saveFile = open(csvFile, 'a')   # reopen csv file
                     saveFile.write(saveLine)        # append the saved row
                     saveFile.close()
                     '''
                     # Var-dependent subplot formatting
                     if var == vars_mx[0]:
                            ax.set_ylabel('mm')
                            ax.text(.1, .8,
                                   str(round((end-start)*coef[0,0],2))+'mm/40yr',
                                   transform=ax.transAxes,
                                   fontsize=24,
                                   color='red')
                     elif var == vars_mx[1]: # cannot figure out how to combine cols_mx[0:2]
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
                     '''
                     plt.savefig(str(key)+'_'+col+'_'+month_str[month-1]+'-mm')
                     '''
# %%
# Return recorded coefficients into dictionary
dfCoef = pd.read_csv(csvFile, delimiter=',', usecols=headerList)
dictCoef = {key: dfCoef[dfCoef['key'] == key] for key in keylist_mx}

# Reset index for each dataframe to make appending easier
for key in keylist_mx:
       dictCoef[key].reset_index(drop=True, inplace=True)

# %%
# Monte Carlo function to generate randomized sample of observed values for given timeframe.
def monteCarloGenerator(obsValueList):
       global coef   # linear regression variable will be added to list in iterator

       tX = [] # list to collect count of years for x-axis
       vY = [] # list to collect randomized observed values for y-axis

       currentYear = 1                    # counter to keep track of years
       listLen = len(obsValueList)        # create limit of rolls and range of position values
                                          # not all station/variable/month datasets are same size
       while currentYear <= listLen:
              roll = randint(0,(listLen-1))             # generate random index place value
              selectedValue = obsValueList[roll]       # select corresponding precip value from list
              tX.append(currentYear)                    # add year value to list
              vY.append(selectedValue)                 # add precip value to list

              currentYear += 1
              
       # Calculate the linear regression
       # merge selectedValue and counter lists into dict
       selValDf = pd.DataFrame({'year':tX,'variable':vY})       # convert dictionary into dataframe
       selValDf = selValDf.dropna()              # drop NaN-bearing rows from dataframe

       x_data = selValDf['year'].values.reshape(selValDf.shape[0],1)   # prep data for linreg
       y_data = selValDf['variable'].values.reshape(selValDf.shape[0],1)

       reg = linear_model.LinearRegression().fit(x_data, y_data)
       coef = reg.coef_ * listLen  # define linreg trend as coef to be plot and saved in iterator
                                   # multiply coef by listLen variable for variables w/ < 40 yrs of data

# # %%
# # Automate the iterator to run through all station/variable/month MCA distributions
# # get start datetime
# startTime = datetime.now()

# # keylist_mx = [26057]      # test values to play with plot output
# # vars_mx = ['tmax']

# for key in keylist_mx:
       
#        df = dictMonthly[key]       # Set object name for ease of reading
#        lrcSdList = []              # reset SD list for each key and append to dictCoef
#        lrcMeanList = []            # reset mean list for each key and append to dictCoef

#        for var in vars_mx:

#               for month in range(1,13):
#               #for month in range(1,2):
#                      # Select data from observed record for the iterator
#                      dataset = df[(df.index.month==month) &\
#                                   (df.variable==var)].measurement.tail(40).values.tolist()

#                      # Select observed linreg coef to plot on MCA distribution
#                      obsCoef = dictCoef[key][(dictCoef[key].variable==var) &\
#                                              (dictCoef[key]['month']==month)]['coef'].values[0]

#                      sampSize = 10000     # number of iterations for MCA
#                      counter = 1          # counter to keep track of iterated distributions
#                      linRegCoef = []      # create list for storing generated linreg coefs

#                      # iterate Monte Carlo simulator code
#                      while counter <= sampSize:  # iterate to chosen sample size
#                             monteCarloGenerator(dataset)
#                             linRegCoef.append(coef[0,0])
                    
#                             counter += 1

#                      # collect information about generated linreg statistics (SD and mean)
#                      coefSeries = pd.Series(linRegCoef)                      # linregCoef to Series
#                      lrcSD, lrcMean = coefSeries.std(), coefSeries.mean()    # define SD and mean

#                      lrcSdList.append(lrcSD)                                 # append SD to list
#                      lrcMeanList.append(lrcMean)                             # append mean to list

#                      # calculate percent chance of generating observed trend, or higher
#                      chanceCount = 0

#                      for i in range(len(coefSeries)):
#                             if obsCoef < 0:                    # for (-) historical trends
#                                    if obsCoef > coefSeries[i]:
#                                           chanceCount += 1
#                             else:                              # for (+) historical trends
#                                    if obsCoef < coefSeries[i]:
#                                           chanceCount += 1

#                      percentChance = chanceCount/len(coefSeries)*100

#                      # plot distribution of coefficients onto histogram
#                      ax = coefSeries.plot.hist(bins=50, label='_nolegend_') # generate histogram of linregCoef
#                      ax.axvline(obsCoef, color='r', label='historical trend')     # plots corresponding linregCoef

#                      if var == vars_mx[0]:
#                             textstr = '\n'.join((
#                                    r'historical trend = %.2f%s' % (obsCoef, 'mm/40yr'),
#                                    r'MC-generation chance = %.2f%s' % (percentChance, '%'),
#                                    r'$\sigma=%.2f$' % (lrcSD, )))
#                      elif var == vars_mx[1]:
#                             textstr = '\n'.join((
#                                    r'historical trend = %.2f%s' % (obsCoef, 'mm/40yr'),
#                                    r'MC-generation chance = %.2f%s' % (percentChance, '%'),
#                                    r'$\sigma=%.2f$' % (lrcSD, )))
#                      else:
#                             textstr = '\n'.join((
#                                    r'historical trend = %.2f%s' % (obsCoef, degree_sign+'C/40yr'),
#                                    r'MC-generation chance = %.2f%s' % (percentChance, '%'),
#                                    r'$\sigma=%.2f$' % (lrcSD, )))

#                      props = dict(boxstyle='round', facecolor='lightsteelblue', alpha=0.5)

#                      # place a text box in upper left in axes coords
#                      ax.text(0.05, 0.92, textstr, transform=ax.transAxes, fontsize=12,
#                             verticalalignment='top', bbox=props)
#                      # ax.text((obsCoef), 40,
#                      #               str(round(obsCoef,2))+'mm/40yr',
#                      #               #transform=ax.transAxes,
#                      #               fontsize=16,
#                      #               color='red',
#                      #               horizontalalignment='center')
#                      ax.set_xlabel(var)
#                      ax.set_ylabel('Count')
#                      ax.set_title('Monte Carlo Analysis of '+month_str[month-1]+' '+var+\
#                                   '\nClimate Station '+str(key)+', n='+str(sampSize), fontsize=12)
#                      plt.legend(loc='upper right')
#                      plt.savefig('mcaPlots/'+str(key)+'-'+var+'-'+month_str[month-1]+'_mca')
#                      plt.show()
                     
#        # add SD and mean to dictCoef dataframes
#        dfStats = pd.DataFrame({'sd': lrcSdList, 'mean': lrcMeanList}) # convert sd/mean lists to df
#        dictCoef[key] = dictCoef[key].join(dfStats, how='left')        # join above df to dictCoef
#        dictCoef[key][['key', 'month']] = dictCoef[key][['key','month']].astype(int) # reset key/month to ints

# endTime = datetime.now()
# elapsedTime = endTime - startTime
# print('Execution time:', elapsedTime)

# %%
# Organize precip data into wet/dry seasons
# Select precip data and organize into a new dictionary
#dictPrecip = {key: dictMonthly[key][dictMonthly[key].variable == 'precip'] for key in keylist_mx}

# Create function to assign seasonality of the measurement based on the month
season = lambda row: 'smr' if 6 <= row['month'] <= 9 else\
                    ('wtr' if row['month'] <= 3 else\
                    ('wtr' if row['month'] >= 11 else np.nan))

# Create dictionary to receive updated dataframes
dictPrecip = {}

for key in keylist_mx:
       df = dictMonthly[key][dictMonthly[key].variable == 'precip'].copy()   # .copy() prevents settingwithcopy warning
       df['season'] = df.apply(season, axis=1)                               # create col to receive season
       data = {key: df}                                                      # dict object to be updated
       dictPrecip.update(data)                                               # update created dict

# %%
# Calculate rainfall for winter frontal storm seasons for all stations
# Select precip data from QC'd database
dictPrecip = {key: dictMelt[key][dictMelt[key].variable == 'precip'] for key in keylist_mx}

# Set up master dictionary to receive year & precipSum entries for all stations
dictWinterRain = {}

for key in keylist_mx:
       df = dictPrecip[key]                             # simplify database for reference
       yearList = df.index.year.unique().tolist()       # generate list of available years
       stationData = {}                                 # create dict to hold precipSums for single station

       for year in yearList:
              # Create mask of desired dates for Winter rain-season
              mask = (df.index >= dt.datetime(year,11,1)) & (df.index <= dt.datetime(year+1,3,31))
              rainfall = df.loc[mask,['measurement']].sum()    # sum precip measurements from each day
              winterPrecip = {year:rainfall[0]}                # generate year/precipSum entry
              stationData.update(winterPrecip)                 # update station data with winter sum
       dictStation = {key:stationData}           # generate station key/data entry
       dictWinterRain.update(dictStation)        # update dict with data for entire station
# %%
# Calculate rainfall for winter frontal storm seasons for all stations
# Select precip data from QC'd database
dictPrecip = {key: dictMelt[key][dictMelt[key].variable == 'precip'] for key in keylist_mx}

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


# %%
for key in keylist_mx:
       index = 0
       while index > 48:
              if 'obs linregCoef > mean + 2*SD':
                     'return some value'
              elif 'obs linregCoef < mean - 2*SD':
                     'return another value'
              else:
                     break
              index += 1

# %%
# proving grounds for MCA code
# Resample data to a monthly mean
dict_mm_mx = {key: dict_mx[key][vars_mx].resample('M').mean() for key in keylist_mx}

# Add year and month columns for each monthly mean to make graphing simpler
for key in keylist_mx:
       dict_mm_mx[key]['year'] = dict_mm_mx[key].index.year
       dict_mm_mx[key]['month'] = dict_mm_mx[key].index.month


# %%
