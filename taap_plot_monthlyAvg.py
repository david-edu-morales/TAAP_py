# %%
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
from sklearn import linear_model
import csv
import seaborn as sns
sns.set(rc={'figure.figsize':(11, 4)})

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys
varsAvg_mx = ['evap', 'tmax', 'tmin']                   # specifiy variables to be resampled
csvFile = 'climateStationTrends_monthlyAvg.csv'         # csv filename to collect linRegCoefs
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
# Determine the monthly averages (Tn, Tx, and ET) from the climatological data
dictMonthlyAvg = {}     # create dictionary to receive for loop outputs

for key in keylist_mx:
    grouped = dictCleanData[key].groupby('variable')                # group data by variable

    # First, calculate monthly averages
    monthlyAvg = grouped.resample('M')[['measurement']].mean()      # calc monthly mean of all variables
    monthlyAvg = monthlyAvg.loc[['evap', 'tmax', 'tmin']]           # drop the resampled precip data
    monthlyAvg = monthlyAvg.reset_index(level='variable')           # return multiindex to 'variable' column

    # Second, reset 'month' and 'year' columns
    monthlyAvg['month'] = monthlyAvg.index.month
    monthlyAvg['year'] = monthlyAvg.index.year

    # Third, create element to append to dictionary
    data = {key: monthlyAvg}                                        # temporary element for update
    dictMonthlyAvg.update(data)                                     # append element to dictionary

# %%
# Create cleaned-data csv files
for key in keylist_mx:
       dictMonthlyAvg[key].to_csv(str(key)+'_monthlyAvg.csv')

# %%
# Re-create the 12-month plots for each station/variable using the quality-controlled data

with open(csvFile, 'w') as file:       # set mode to write w/ truncation
       dw = csv.DictWriter(file, delimiter=',',
                           fieldnames=headerList)
       dw.writeheader()

# Set up data & variables
start, end = 1976, 2016 # set time frame to last forty years

for key in keylist_mx:
       df = dictMonthlyAvg[key]       # rename working database for ease of reading      

       for var in varsAvg_mx:

              fig = plt.figure(figsize=(24,16))
              fig.subplots_adjust(hspace=0.2, wspace=0.2)

              # Set figure title
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
                     
                     # Save the observed trends to a csv to be plotted on monte carlo distribution
                     saveLine = '\n'+str(key)+','+str(var)+','+str(month)+','+str(40*coef[0,0])

                     saveFile = open(csvFile, 'a')   # reopen csv file
                     saveFile.write(saveLine)        # append the saved row
                     saveFile.close()
                     
                     # Set number of x-axis tick marks to max (5) and only as integers
                     ax.xaxis.set_major_locator(MaxNLocator(5, integer=True))

                     # Var-dependent subplot formatting
                     if var == varsAvg_mx[0]:
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
                     
              plt.savefig('graphs/avgPlots/'+str(key)+'_'+var+'-avg')

# %%
