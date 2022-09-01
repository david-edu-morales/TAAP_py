# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, DateFormatter

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
plt.subplots_adjust(hspace=0.15)
plt.suptitle('Percent chance Monte Carlo-generated trend\nis greater than historical trend')
fig.text(0.08, 0.5, '% chance', va='center', rotation='vertical', fontsize=16)
plt.xlabel('Month', fontsize=15)
plt.xlim([.9,12.1])

for n, var in enumerate(varsAvg_mx):
    ax = plt.subplot(3, 1, n+1)

    for key in keylist_mx:
        mask = (dictCoefAvg[key].variable == var)
        df = dictCoefAvg[key].loc[mask].set_index('month')
        x = df.index
        y = df.chance
        plt.title(var.capitalize(), fontsize=12, fontweight='bold')
        plt.plot(x,y, marker='o', fillstyle='full', markerfacecolor='white', label='Station '+str(key))
        plt.xticks(np.arange(min(x), max(x)+1, 1.0))
        plt.yticks(np.arange(0, 50, 10.0))
        plt.hlines(5, xmin=0, xmax=12.1, colors='k', linestyles='dashed', alpha=0.25)

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, bbox_to_anchor=(.2625,.88))

plt.savefig('graphs/prctChance-avg')
plt.show()


    # %%
