# %%
import matplotlib
import matplotlib.pyplot as plt
import csv
from mpl_toolkits.mplot3d import Axes3D

# %%
fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')

def graph():
    with open('monteCarloLiberal.csv','r') as montecarlo: # 'r' signifies read
        datas = csv.reader(montecarlo, delimiter=',')

        for eachLine in datas:
            percentROI = float(eachLine[0])
            wagerSizePercent = float(eachLine[1])
            wagerCount = float(eachLine[2])
            pcolor = eachLine[3]

            ax.scatter(wagerSizePercent, wagerCount, percentROI, color=pcolor)

            ax.set_xlabel('Wager percent size')
            ax.set_ylabel('Wager count')
            ax.set_zlabel('Percent ROI')
            
    plt.show()

graph()
# %%