# %%
import random
import matplotlib
import matplotlib.pyplot as plt
import time

# %%
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

def doubler_bettor(funds, initial_wager,wager_count):
    value = funds
    wager = initial_wager
    global broke_count
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
                if value < 0:
                    #print('we went broke after', currentWager,'bets')
                    broke_count+=1
                    break
        elif previousWager == 'loss':
            #print('we lost the last one, so we will be smart and double')
            if rollDice():
                wager = previousWagerAmount * 2
                #print('we won', wager)
                value+=wager
                #print(value)
                wager = initial_wager
                previousWager = 'win'
                wX.append(currentWager)
                vY.append(value)
            else:
                wager = previousWagerAmount * 2
                #print('we lost', wager)
                value -= wager
                if value < 0:
                    #print('we went broke after', currentWager, 'bets')
                    broke_count+=1
                    break
                #print(value)
                previousWager = 'loss'

                previousWagerAmount = wager
                wX.append(currentWager)
                vY.append(value)
        currentWager += 1

    #print(value)
    plt.plot(wX,vY)

xx = 0
broke_count = 0

while xx < 100:
    doubler_bettor(10000, 100, 100)
    xx+=1

print('death rate:', (broke_count/float(xx)) * 100)
print('survival rate:', 100-((broke_count/float(xx))*100))

plt.axhline(0, color = 'r')

plt.show()

time.sleep(45)

# %%
def simple_bettor(funds, initial_wager,wager_count):
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

    if value < 0:
        value = 'broke'
    #print('Funds:', value)

    plt.plot(wX, vY)

x = 0

while x < 100:
    simple_bettor(10000, 100, 10000)
    x += 1

plt.ylabel('Account Value')
plt.xlabel('Wager Count')
plt.show()

# %%
x = 0

while x < 100:
    result = rollDice()
    print(result)
    x+=1

# %%
