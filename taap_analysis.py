# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, DateFormatter
import datetime as dt
import seaborn as sns

sns.set(rc={'figure.figsize':(11, 4)})

# %%
# Set the station IDs
keylist_mx = [26013, 26057, 26164]
varsAvg_mx = ['evap', 'tmin', 'tmax']

# %%
# Monte Carlo Simulation analysis
# PRECIPITATION DATA:
filenameDict = {keylist_mx[key]: 'data/'+str(keylist_mx[key])+'_coefData-sum.csv' for key in range(len(keylist_mx))}
# Create a dictionary of keys and corresponding dataframes
dictCoefSum = {key: pd.read_csv(filename).drop(['Unnamed: 0'], axis=1) for (key, filename) in filenameDict.items()}

# TX, TN, ET DATA:
filenameDict = {keylist_mx[key]: 'data/'+str(keylist_mx[key])+'_coefData-avg.csv' for key in range(len(keylist_mx))}
# Create a dictionary of keys and corresponding dataframes
dictCoefAvg = {key: pd.read_csv(filename).drop(['Unnamed: 0'], axis=1) for (key, filename) in filenameDict.items()}

# %%
df = dictCoefAvg[26057]

x = df['month']
y = df[['variable','chance']]

for var in varsAvg_mx:
    mask = (dictCoefAvg[26057].variable == var)
    df = dictCoefAvg[26057].loc[mask].set_index('month')
    df['chance'].plot(ylabel='chance')

# %%
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(12, 6.5), sharex=True, sharey=True)
plt.subplots_adjust(hspace=0.2)
plt.suptitle('Percent chance Monte Carlo-generated trend\nis greater than historical trend')
fig.text(0.08, 0.5, '% chance', va='center', rotation='vertical', fontsize=16)
plt.xlabel('Month', fontsize=15)

for n, var in enumerate(varsAvg_mx):
    ax = plt.subplot(3, 1, n+1)

    for key in keylist_mx:
        # Select subset of dataframe for plotting
        mask = (dictCoefAvg[key].variable == var)           # bool mask set to looped variable
        df = dictCoefAvg[key].loc[mask].set_index('month')  # dataset from bool index and reset index
        df.index = pd.to_datetime(df.index, format='%m')    # convert index to datetimeindex

        x = df.index
        y = df.chance

        plt.title(var.capitalize(),             # set subplot title
                  fontsize=12,
                  fontweight='bold')
        plt.plot(x, y,                          # plot data
                 marker='o',
                 fillstyle='full',
                 markerfacecolor='white',
                 label='Station '+str(key))
        plt.hlines(5, xmin=dt.date(1900,1,1),   # plot 5% threshold for significant data
                      xmax=dt.date(1900,12,31),
                      colors='k',
                      linestyles='dashed',
                      alpha=0.25)
        plt.yticks(np.arange(0, 50, 10.0))      # edit y-ticks for clarity

        ax.set_xlim([dt.date(1899, 12, 31), dt.date(1900, 12, 2)])  # set x-axis limit

        # Rename datetime x-ticks to the first letter of each month
        month_fmt = DateFormatter('%b')
        def m_fmt(x, pos=None):
            return month_fmt(x)[0]
        ax.xaxis.set_major_locator(MonthLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(m_fmt))

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, bbox_to_anchor=(.2625,.88))

plt.savefig('graphs/prctChance-avg')
plt.show()

# %%
