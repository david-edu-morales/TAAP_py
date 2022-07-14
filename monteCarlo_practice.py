# %%
import random
import matplotlib
import matplotlib.pyplot as plt
import time

from urllib3 import Retry
from multi_bettor import *

# %%
lower_bust = 31.235     # after running 1e6 times, this was the doubler bust rate
higher_profit = 63.208  # after running 1e6 times, this was the doubler profit rate

sampleSize = 1000
startingFunds = 100000
wagerSize = 100
wagerCount = 1000

'''
def rollDice():
    roll = random.randint(1, 100)

    if roll == 100:
        #print(roll, 'roll was 100, you lose. What are the odds? Play again!')
        return False

    elif roll <= 50:
        #print(roll, 'roll was 1-50, you lose. Play again!')
        return False

    elif 100 > roll > 50:
        #print(roll, 'roll was 51-99, you win! Play more!')
        return True
'''

def rollDice():
    roll = random.randint(1, 100)

    if roll <= 50:      # losing roll
        return False

    elif roll >= 50:     # winning roll
        return True

def dAlembert(funds, initial_wager, wager_count):
    
    global Ret
    global da_busts
    global da_profits

    value = funds
    wager = initial_wager
    currentWager = 1
    previousWager = 'win'
    previousWagerAmount = initial_wager

    while currentWager <= wager_count:
        if previousWager == 'win':
            if wager == initial_wager:
                pass
            else:
                wager -= initial_wager
            
            #print('current wager', wager, 'value', value)

            if rollDice():
                value += wager
                previousWagerAmount = wager
                #print('we won, current value:', value)
            else:
                value -= wager
                previousWager = 'loss'
                #print('we lost, current value:', value)
                previousWagerAmount = wager
                
                if value <= 0:
                    da_busts+=1
                    break

        elif previousWager == 'loss':
            wager = previousWagerAmount + initial_wager
            if (value - wager) <= 0:
                wager = value

            #print('lost the last wager, current wager:', wager, 'value', value)

            if rollDice():
                value += wager
                previousWager = 'win'
                #print('we won, current value:', value)
                previousWagerAmount = wager
            else:
                value -= wager
                #print('we lost, current value:', value)
                previousWagerAmount = wager

                if value <= 0:
                    da_busts+=1
                    break

        currentWager += 1

    if value > funds:
        da_profits+=1

    Ret += value

def multiple_bettor(funds, initial_wager, wager_count):
    global multiple_busts
    global multiple_profits

    value = funds
    wager = initial_wager
    wX = []
    vY = []

    currentWager = 1
    previousWager = 'win'
    previousWagerAmount = initial_wager

    while currentWager <= wager_count:
        if previousWager == 'win':
            #print('we won the last wager, great')
            if rollDice():
                value+=wager
                #print(value)
                wX.append(currentWager)
                vY.append(value)
            else:
                value -= wager
                previousWager = 'loss'
                #print (value)
                previousWagerAmount = wager
                wX.append(currentWager)
                vY.append(value)
                if value <= 0:
                    #print('we went broke after', currentWager,'bets')
                    multiple_busts+=1
                    break

        elif previousWager == 'loss':
            #print('we lost the last one, so we will be smart and double')
            if rollDice():
                wager = previousWagerAmount * random_multiple

                if (value - wager < 0):
                    wager = value
                #print('we won', wager)
                value+=wager
                #print(value)
                wager = initial_wager
                previousWager = 'win'
                wX.append(currentWager)
                vY.append(value)
            else:
                wager = previousWagerAmount * random_multiple

                if (value - wager < 0):
                    wager = value
                #print('we lost', wager)
                value -= wager
                previousWagerAmount = wager
                wX.append(currentWager)
                vY.append(value)
                if value <= 0:
                    #print('we went broke after', currentWager, 'bets')
                    multiple_busts+=1
                    break
                #print(value)
                previousWager = 'loss'

        currentWager += 1

    #print(value)
    #plt.plot(wX,vY,color)
    if value > funds:
        multiple_profits += 1

def doubler_bettor(funds, initial_wager,wager_count, color):
    value = funds
    wager = initial_wager
    global doubler_busts
    global doubler_profits
    wX = []
    vY = []

    currentWager = 1
    previousWager = 'win'
    previousWagerAmount = initial_wager

    while currentWager <= wager_count:
        if previousWager == 'win':
            #print('we won the last wager, great')
            if rollDice():
                value+=wager
                #print(value)
                wX.append(currentWager)
                vY.append(value)
            else:
                value -= wager
                previousWager = 'loss'
                #print (value)
                previousWagerAmount = wager
                wX.append(currentWager)
                vY.append(value)
                if value <= 0:
                    #print('we went broke after', currentWager,'bets')
                    doubler_busts+=1
                    break

        elif previousWager == 'loss':
            #print('we lost the last one, so we will be smart and double')
            if rollDice():
                wager = previousWagerAmount * 2

                if (value - wager < 0):
                    wager = value
                #print('we won', wager)
                value+=wager
                #print(value)
                wager = initial_wager
                previousWager = 'win'
                wX.append(currentWager)
                vY.append(value)
            else:
                wager = previousWagerAmount * 2

                if (value - wager < 0):
                    wager = value
                #print('we lost', wager)
                value -= wager
                previousWagerAmount = wager
                wX.append(currentWager)
                vY.append(value)
                if value <= 0:
                    #print('we went broke after', currentWager, 'bets')
                    doubler_busts+=1
                    break
                #print(value)
                previousWager = 'loss'

                
        currentWager += 1

    #print(value)
    plt.plot(wX,vY,color)
    if value > funds:
        doubler_profits += 1

#time.sleep(45)

def simple_bettor(funds, initial_wager,wager_count, color):
    global simple_busts
    global simple_profits
    value = funds
    wager = initial_wager

    wX = []
    vY = []

    currentWager = 1

    while currentWager <= wager_count:
        if rollDice():
            value += wager
            wX.append(currentWager)
            vY.append(value)
        else:
            value -= wager
            wX.append(currentWager)
            vY.append(value)

        currentWager += 1

    if value <= 0:
        value = 0
        simple_busts+=1
    #print('Funds:', value)

    plt.plot(wX, vY, color)
    if value > funds:
        value = 0
        simple_profits += 1

x = 0

Ret = 0.0
da_profits = 0.0
da_busts = 0.0
daSampSize = 10000

counter = 1

while counter <= daSampSize:
    dAlembert(startingFunds, wagerSize, wagerCount)
    counter +=1 

print('Total invested', daSampSize*startingFunds)
print('Total return:', Ret)
print('ROI', Ret - (daSampSize*startingFunds))
print('Bust rate:', (da_busts/daSampSize)*100.00)
print('Profit rate:', (da_profits/daSampSize)*100.00)

# %%
