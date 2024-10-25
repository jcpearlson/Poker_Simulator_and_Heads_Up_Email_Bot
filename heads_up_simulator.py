import math
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime
from helper_functions import *


def runSimulation(data,challenge_end=3000,num_sims= 10000):

    logMsg(f'running sim with end={challenge_end} hands and {num_sims} sims')

    # run simulations
    def bootstrap_simulation(player_data, n_hands=int(challenge_end - data['Hands'].sum()), n_simulations=10000,target_vol=(4.00)):

        # determine how much vol to add to player_data
        current_vol = player_data.std()

        # Calculate noise volatility needed to achieve the target volatility only adds vol does not remove vol.
        addNoise = False
        if current_vol < target_vol:
            addNoise = True
            noise_to_add = np.sqrt(target_vol**2 - current_vol**2)
            logMsg(f'adding vol to simulation: Target Vol: {target_vol:4f}, Current Vol: {current_vol:4f}, Added Vol (noise): {noise_to_add:4f}')
     
        cumulative_results = []
        for _ in range(n_simulations):

            # generate a sample value
            sample = np.random.choice(player_data, size=n_hands, replace=True)

            # add noise into sample to increase vol to target
            if addNoise:
                noise = np.random.normal(0, noise_to_add, size=n_hands) 

            sample_with_noise = sample+noise
            cumulative_sample = np.cumsum(sample_with_noise)
            cumulative_results.append(cumulative_sample)
        return np.array(cumulative_results)

    # Run simulations for both players
    josh_cumulative = bootstrap_simulation(data['Josh_profit_per_hand'])
    jimmy_cumulative = bootstrap_simulation(data['Jimmy_profit_per_hand'])

    # Calculate statistics for each hand (cumulative)
    def calculate_cumulative_stats(cumulative_results):
        mean = np.mean(cumulative_results, axis=0)
        ci_lower = np.percentile(cumulative_results, 2.5, axis=0)
        ci_upper = np.percentile(cumulative_results, 97.5, axis=0)
        return mean, ci_lower, ci_upper

    # Get mean and confidence intervals for both players
    josh_mean, josh_ci_lower, josh_ci_upper = calculate_cumulative_stats(josh_cumulative)
    cumWinningsJo = data['Josh Cumulative Winnings'].iloc[-1]
    josh_mean = josh_mean + cumWinningsJo
    josh_ci_lower = josh_ci_lower + cumWinningsJo
    josh_ci_upper = josh_ci_upper + cumWinningsJo
    josh_cumulative = josh_cumulative + cumWinningsJo

    jimmy_mean, jimmy_ci_lower, jimmy_ci_upper = calculate_cumulative_stats(jimmy_cumulative)
    cumWinningsJi = -1*cumWinningsJo
    jimmy_mean = jimmy_mean + cumWinningsJi
    jimmy_ci_lower = jimmy_ci_lower + cumWinningsJi
    jimmy_ci_upper = jimmy_ci_upper + cumWinningsJi
    jimmy_cumulative = jimmy_cumulative + cumWinningsJi

    # total hands played so far
    total_hands = int(data['Cumulative Hands'].iloc[-1])

    # create shift for simulation versus origional data
    start_x = np.linspace(1, total_hands,total_hands)
    hands_left = challenge_end-total_hands
    shifted_x = np.linspace(total_hands+1,challenge_end,hands_left)

    # Create a graph showing Monte Carlo simulations with confidence intervals
    plt.figure(figsize=(12, 6))

    # dark_background option 
    # plt.style.use('dark_background')

    # Plot Josh's mean and confidence interval
    plt.plot(shifted_x,josh_mean, color='black', label="Josh's Average")
    plt.fill_between(shifted_x, josh_ci_lower, josh_ci_upper, color='blue', alpha=0.3, label="Josh's 95% CI")
    plt.plot(data['Cumulative Hands'], data['Josh Cumulative Winnings'], label='Josh Cumulative Winnings', marker='o')

    # Plot Jimmy's mean and confidence interval
    plt.plot(shifted_x,jimmy_mean, color='black', label="Jimmy's Average")
    plt.fill_between(shifted_x, jimmy_ci_lower, jimmy_ci_upper, color='red', alpha=0.3, label="Jimmy's 95% CI")
    plt.plot(data['Cumulative Hands'], data['Jimmy Cumulative Winnings'], label='Jimmy Cumulative Winnings ', marker='s')\

    # Plot Josh's simulations (only 20 of them)
    for sim in josh_cumulative[:20]:
        plt.plot(shifted_x,sim, color='blue', alpha=0.3)
    josh_avg = np.mean(josh_cumulative, axis=0)

    # Plot Jimmy's simulations (only 20 of them)
    for sim in jimmy_cumulative[:20]:
        plt.plot(shifted_x,sim, color='red', alpha=0.3)
    jimmy_avg = np.mean(jimmy_cumulative, axis=0)


    plt.title('Monte Carlo Simulations of Cumulative Profits with 95% Confidence Interval 10000 sims, 20 plotted')
    plt.xlabel('Number of Hands')
    plt.ylabel('Cumulative Profit ($)')
    plt.legend(loc='upper left')
    plt.grid(True)

    # Add horizontal line at y=0
    plt.axhline(y=0, color='black', linestyle='-')

    # add more ticks 
    plt.xticks(np.arange(0, challenge_end+1, 250))

    plt.tight_layout()

    return plt

def getTimeLeftDays(data:pd.DataFrame=read_csv())->int:
    
    # how long has the challenge taken so far
    month,day,year = data['Date'].iloc[0].split('/')

    start = datetime(int('20'+year),int(month),int(day))

    month,day,year = data['Date'].iloc[-1].split('/')
    end = datetime(int('20'+year),int(month),int(day))

    difference = end-start 
    days = difference.days

    # total hands played
    total_hands_played = data['Cumulative Hands'].iloc[-1]

    # days/hand
    days_per_hand = days / total_hands_played
    
    # how many hands left * days/hand
    days_left = (3000-total_hands_played) *days_per_hand

    return int(math.ceil(days_left))

def getBody(data:pd.DataFrame=read_csv())->str:
    
    total_hands_played = data['Cumulative Hands'].iloc[-1]
    jimmy_cumulative_winnings = data['Jimmy Cumulative Winnings'].iloc[-1]
    jimmy_profit_per_hand = jimmy_cumulative_winnings/total_hands_played
    
    josh_cumulative_winnings = data['Josh Cumulative Winnings'].iloc[-1]
    josh_pph = josh_cumulative_winnings/total_hands_played

    # return string for email
    return (
        """Hello,\n\nI hope everyone has had a fantastic week. I am here to provide updates on Jimmy and Josh\'s heads up challenge. """
        """Attached are the current standings and a simulation out to the end of the 3,000 hand challenge. \n\n"""
              f'Total hands played: {int(total_hands_played)} \n\n'
              f'Jimmy total = ${round(jimmy_cumulative_winnings,0)} \n'
              f'Jimmy winnings/hand = ${round(jimmy_profit_per_hand,2)} \n\n'
              f'Josh total = ${round(josh_cumulative_winnings,0)}\n'
              f'Josh winnings/hand = ${round(josh_pph,2)} \n\n'
              f'At the current pace it is expected that the challenge will be finished in {getTimeLeftDays(data)} days! \n'
              f'I hope everyone has a great week ahead. \n\n'
              f'Best,\n'
              f'JoshBot\n\n\n\n'
              "Note: This email is automated to send once weekly, please message sender to remove yourself from list."
    )

# # # Testing Code
# data = read_csv()
# # print(data['Josh_profit_per_hand'])
# runSimulation(data).savefig('testfig.png')