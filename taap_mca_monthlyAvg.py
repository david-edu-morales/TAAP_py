# %%
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
from sklearn import linear_model
import seaborn as sns

sns.set(rc={'figure.figsize':(11, 4)})

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys
varsAvg_mx = ['tmax', 'tmin','evap']                   # specifiy variables to be resampled
csvFile = 'data/historicalTrends_monthlyAvg.csv'    # csv filename to collect linRegCoefs
headerList = ['key', 'variable', 'month', 'coef']       # header names for csv of linRegCoefs
month_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May','Jun',\
             'Jul','Aug','Sep','Oct','Nov','Dec']       # setup month names for graph
degree_sign = u'\N{DEGREE SIGN}'                        # degree sign code

# %%
# *** MEXICAN CLIMATE STATIONS ***
# Read the files into a df
# Create a dictionary of keys and filenames to call dataframes into another dictionary
filenameDict = {keylist_mx[key]: 'data/'+str(keylist_mx[key])+'_monthlyAvg.csv' for key in range(len(keylist_mx))}

# Create a dictionary of keys and corresponding dataframes
dictMonthlyAvg = {key: pd.read_csv(filename,
                                  index_col = 'date',
                                  parse_dates=True)
                for (key, filename) in filenameDict.items()}

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

# %%
# Return recorded coefficients into dictionary
dfCoef = pd.read_csv(csvFile, delimiter=',', usecols=headerList)
dictCoef = {key: dfCoef[dfCoef['key'] == key] for key in keylist_mx}

# Reset index for each dataframe to make appending easier
for key in keylist_mx:
       dictCoef[key].reset_index(drop=True, inplace=True)

# %%
# Automate the iterator to run through all station/variable/month MCA distributions
# get start datetime
startTime = dt.datetime.now()

for key in keylist_mx:
       
        dfKey = dictMonthlyAvg[key]       # Set object name for ease of reading
        lrcSdList = []              # reset SD list for each key and append to dictCoef
        lrcMeanList = []            # reset mean list for each key and append to dictCoef
        chanceList = []

        for var in varsAvg_mx:

                for month in range(1,13):
                #for month in range(1,2):
                        # Select data from observed record for the iterator
                        df = dfKey[(dfKey.index.month==month) & (dfKey.variable==var)]

                        end = df.index.year[-1]
                        start = end - 39

                        dataset = df.loc[str(start):str(end)].measurement.values.tolist()

                        # Select observed linreg coef to plot on MCA distribution
                        obsCoef = dictCoef[key][(dictCoef[key].variable==var) &\
                                                (dictCoef[key]['month']==month)]['coef'].values[0]
                                                
                        sampSize = 10000     # number of iterations for MCA
                        counter = 1          # counter to keep track of iterated distributions
                        linRegCoef = []      # create list for storing generated linreg coefs

                        # Iterate Monte Carlo simulator code
                        while counter <= sampSize:  # iterate to chosen sample size
                                monteCarloGenerator(dataset)
                                linRegCoef.append(coef[0,0])
                
                                counter += 1

                        # Collect information about generated linreg statistics (SD and mean)
                        coefSeries = pd.Series(linRegCoef)                      # linregCoef to Series
                        lrcSD, lrcMean = coefSeries.std(), coefSeries.mean()    # define SD and mean

                        lrcSdList.append(lrcSD)                                 # append SD to list
                        lrcMeanList.append(lrcMean)                             # append mean to list

                        # Calculate percent chance of generating observed trend, or higher
                        chanceCount = 0

                        for i in range(len(coefSeries)):
                                if obsCoef < 0:                    # for (-) historical trends
                                        if obsCoef > coefSeries[i]:
                                                chanceCount += 1
                                else:                              # for (+) historical trends
                                        if obsCoef < coefSeries[i]:
                                                chanceCount += 1

                        percentChance = chanceCount/len(coefSeries)*100
                        chanceList.append(percentChance)                        # add to chanceList
                        
                        # plot distribution of coefficients onto histogram
                        ax = coefSeries.plot.hist(bins=50, label='_nolegend_') # generate histogram of linregCoef
                        ax.axvline(obsCoef, color='r', label='historical trend')     # plots corresponding linregCoef
                        if var == varsAvg_mx[-1]:
                                textstr = '\n'.join((
                                r'historical trend = %.2f%s' % (obsCoef, 'mm/40yr'),
                                r'MC-generation chance = %.2f%s' % (percentChance, '%'),
                                r'$\sigma=%.2f$' % (lrcSD, )))
                        else:
                                textstr = '\n'.join((
                                r'historical trend = %.2f%s' % (obsCoef, degree_sign+'C/40yr'),
                                r'MC-generation chance = %.2f%s' % (percentChance, '%'),
                                r'$\sigma=%.2f$' % (lrcSD, )))

                        props = dict(boxstyle='round', facecolor='lightsteelblue', alpha=0.5)

                        # place a text box in upper left in axes coords
                        ax.text(0.05, 0.92, textstr, transform=ax.transAxes, fontsize=12,
                                verticalalignment='top', bbox=props)

                        ax.set_xlabel(var)
                        ax.set_ylabel('Count')
                        ax.set_title('Monte Carlo Analysis of '+month_str[month-1]+' '+var+\
                                '\nClimate Station '+str(key)+', n='+str(sampSize), fontsize=12)
                        plt.legend(loc='upper right')
                        plt.savefig('graphs/mcaPlots/'+str(key)+'-'+var+'-'+month_str[month-1]+'_mca')
                        plt.show()
                        
                        print(str(key)+'/'+var+'/'+str(month)+': stats completed')
                print('_________________________')

        # add SD and mean to dictCoef dataframes
        dfStats = pd.DataFrame({'sd': lrcSdList, 'mean': lrcMeanList, 'chance': chanceList}) # convert sd/mean lists to df
        dictCoef[key] = dictCoef[key].join(dfStats, how='left')        # join above df to dictCoef
        dictCoef[key][['key', 'month']] = dictCoef[key][['key','month']].astype(int) # reset key/month to ints

endTime = dt.datetime.now()
elapsedTime = endTime - startTime
print('Execution time:', elapsedTime)

# %%
# Create cleaned-data csv files
for key in keylist_mx:
       dictCoef[key].to_csv('data/'+str(key)+'_coefData-avg.csv')

# %%