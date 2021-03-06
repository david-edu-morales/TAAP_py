# %%
from datetime import datetime
from dfmgmt import *
import matplotlib as mpl
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
cols_mx = ['precip', 'evap', 'tmax', 'tmin']            # specifiy columns to be resampled
csvFile = 'climateStationTrends_taap.csv'               # csv filename to collect linRegCoefs
csvFileMx = 'climateStationTrends_taap_mx.csv'
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
# Resample data to a monthly mean
dict_mm_mx = {key: dict_mx[key][cols_mx].resample('M').mean() for key in keylist_mx}

# Add year and month columns for each mensual mean to make graphing simpler
for key in keylist_mx:
       dict_mm_mx[key]['year'] = dict_mm_mx[key].index.year
       dict_mm_mx[key]['month'] = dict_mm_mx[key].index.month

# %%
# Automate 12-plot monthly mean plot for variables
# Set up csv file to record linear regression trends
with open(csvFile, 'w') as file:       # set mode to write w/ truncation
       dw = csv.DictWriter(file, delimiter=',',
                           fieldnames=headerList)
       dw.writeheader()                                        # add headers to csv

# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years

for key in keylist_mx:

       for col in cols_mx:

              fig = plt.figure(figsize=(24,16))
              fig.subplots_adjust(hspace=0.2, wspace=0.2)
              fig.suptitle("Monthly Mean for "+col+"\nClimate Station "+str(key), fontsize=30)
              
              for month in range(1,13):
                     ax = fig.add_subplot(3,4,month)    # creates a 12-plot fig (3r x 4c)

                     # select data to plot
                     x = dict_mm_mx[key][dict_mm_mx[key].index.month == month].tail(40).index.year
                     y = dict_mm_mx[key][dict_mm_mx[key].index.month == month][col].tail(40)

                     ax.plot(x,y)  # this plots the col values

                     # Col-alike subplot formatting              
                     ax.set_title(month_str[month-1], fontsize=20, fontweight='bold')

                     # Make the linear regression
                     database = dict_mm_mx[key].loc[dict_mm_mx[key]['month']==month][[col,'year']].tail(40)
                     database = database.dropna()

                     x_data = database['year'].values.reshape(database.shape[0],1)
                     y_data = database[col].values.reshape(database.shape[0],1)

                     reg = linear_model.LinearRegression().fit(x_data, y_data)
                     coef = reg.coef_
                     inter= reg.intercept_
                     y_estimate = coef*x_data+inter # y=mx+b, possible option to upgrade

                     ax.plot(x_data,y_estimate) # this plots the linear regression

                     # Save the observed trends to a csv to be plotted on monte carlo distribution
                     saveLine = '\n'+str(key)+','+str(col)+','+str(month)+','+str(40*coef[0,0])

                     saveFile = open(csvFile, 'a')   # reopen csv file
                     saveFile.write(saveLine)        # append the saved row
                     saveFile.close()

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

                     #plt.savefig(str(key)+'_'+col+'_'+month_str[month-1]+'-mm')

# %%
# Return recorded coefficients into dictionary
dfCoef = pd.read_csv(csvFileMx, delimiter=',', usecols=headerList)
dictCoef = {key: dfCoef[dfCoef['key'] == key] for key in keylist_mx}

# Reset index for each dataframe to make appending easier
for key in keylist_mx:
       dictCoef[key].reset_index(drop=True, inplace=True)

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
day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] # "normal" year distro
ly_list = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] # leap-year distro

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
       selValDict = {'year':tX,'variable':vY}    # merge selectedValue and counter lists into dict
       selValDf = pd.DataFrame(selValDict)       # convert dictionary into dataframe
       selValDf = selValDf.dropna()              # drop NaN-bearing rows from dataframe

       x_data = selValDf['year'].values.reshape(selValDf.shape[0],1)   # prep data for linreg
       y_data = selValDf['variable'].values.reshape(selValDf.shape[0],1)

       reg = linear_model.LinearRegression().fit(x_data, y_data)
       coef = reg.coef_     # define linreg trend as coef to be plot and saved in iterator

# %%
# Automate the iterator to run through all station/variable/month MCA distributions
# get start datetime
startTime = datetime.now()

for key in keylist_mx:
       
       tempDf = dictCoef[key]      # shorten name for readability 
       lrcSdList = []              # reset SD list for each key and append to dictCoef
       lrcMeanList = []            # reset mean list for each key and append to dictCoef

       for col in cols_mx:

              for month in range(1,13):
                     # Select data from observed record for the iterator
                     dataset = dict_mm_mx[key][dict_mm_mx[key]['month']==month]\
                               [col].tail(40).values.tolist()

                     # Select observed linreg coef to plot on MCA distribution
                     obsCoef = dictCoef[key][(dictCoef[key]['variable']==col)\
                               & (dictCoef[key]['month']==month)]['coef'].values[0]

                     sampSize = 10        # number of iterations for MCA
                     counter = 1          # counter to keep track of iterated distributions
                     linRegCoef = []      # create list for storing generated linreg coefs

                     # iterate Monte Carlo simulator code
                     while counter <= sampSize:  # iterate to chosen sample size
                            monteCarloGenerator(dataset)
                            linRegCoef.append(40*coef[0,0])
                    
                            counter += 1

                     # collect information about generated linreg statistics (SD and mean)
                     coefSeries = pd.Series(linRegCoef)                      # linregCoef to Series
                     lrcSD, lrcMean = coefSeries.std(), coefSeries.mean()    # define SD and mean

                     lrcSdList.append(lrcSD)                                 # append SD to list
                     lrcMeanList.append(lrcMean)                             # append mean to list

                     '''
                     # plot distribution of coefficients onto histogram
                     
                     ax = coefSeries.plot.hist(bins=50) # generate histogram of linregCoef
                     ax.axvline(obsCoef, color='r')     # plots corresponding linregCoef
                     ax.set_xlabel(col)
                     ax.set_ylabel('Count')
                     ax.set_title('Monte Carlo Analysis of '+month_str[month-1]+' '+col+\
                                  '\nClimate Station '+str(key)+', n='+str(sampSize))
                     plt.show()                         # plots each MCA distribution
                     '''
       # add SD and mean to dictCoef dataframes
       dfStats = pd.DataFrame({'sd': lrcSdList, 'mean': lrcMeanList}) # convert sd/mean lists to df
       tempDf = tempDf.join(dfStats, how='left')                      # join above df to dictCoef
       tempDf[['key', 'month']] = tempDf[['key','month']].astype(int) # reset key/month to ints

endTime = datetime.now()
elapsedTime = endTime - startTime
print('Execution time:', elapsedTime)

# %%
# # Set code for iterator
# marTmax = dict_tmax_cmm_mx[2]['tmax'].tail(40).values.tolist()        # example of target list for while loop
# #dict_tmax_cmm_mx[2]['tmax'].tail(40).plot()                          # sample of actual plot

# # set variables for iterator
# sampSize = 100000 # number of iterations for Monte Carlo simulator
# counter = 1   # counter to keep track of iterated distributions
# linRegCoef = [] # create list for store linreg coefficients

# # iterate monte carlo simulator code
# while counter <= sampSize:  # setting the number of iterations to the chosen sample size
#        monteCarloPrecip(marTmax)
#        linRegCoef.append(40*coef[0,0])
#        #plt.show()    # creates separate graphs for each iteration, comment out for one main plot
       
#        counter += 1

# # plot distribution of coefficients onto histogram
# coefSeries = pd.Series(linRegCoef) # convert list of linreg coefficients to series
# ax = coefSeries.plot.hist(bins=50)
# ax.set_xlabel(degree_sign+'C/40yr')    
# ax.set_title('Monte Carlo Analysis of March tmax\nClimate Station 26057, n=' + str(sampSize))
# # ax.axvline(5.24, color='r') # shows the corresponding linreg coefficient value for 26057/tmax/March

# # get end datetime
# endTime = datetime.now()

# # get execution time
# elapsedTime = endTime - startTime
# print('Execution time:', elapsedTime)


# %%
