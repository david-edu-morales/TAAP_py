# %%
import random

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

def simple_bettor(funds, initial_wager,wager_count):
    value = funds
    wager = initial_wager

    currentWager = 0

    while currentWager < wager_count:
        if rollDice():
            value += wager
        else:
            value -= wager
        
        currentWager += 1

    if value < 0:
        value = 'broke'
    print('Funds:', value)

x = 0

while x < 100:
    simple_bettor(10000, 100, 10000)
    x += 1

# %%
x = 0

while x < 100:
    result = rollDice()
    print(result)
    x+=1

# %%
