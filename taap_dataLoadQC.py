# %%
import pandas as pd

# %%
# Set up variables
keylist_mx = [26013, 26057, 26164]                      # create list of climate station keys

# %%
# *** MEXICAN CLIMATE STATIONS ***
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
       df['key'] = key                    # Add key column
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
dictMelt = {key: dictMelt[key][['variable','measurement','month','year','key']] for key in keylist_mx}

# %%
# Create cleaned-data csv files
for key in keylist_mx:
       dictMelt[key].to_csv('data/'+str(key)+'_clean-data.csv')