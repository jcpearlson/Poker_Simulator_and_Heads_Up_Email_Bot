import re
import math
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime
from helper_functions import *
import requests 


# bernoulli coin flip approximation of poker variance
def bootstrap_simulation_bernoulli(player_data, n_hands, n_simulations=10000):
    # Calculate the mean (win rate) and standard deviation (volatility) of player_data
    current_win_rate = player_data.mean()
    current_vol = player_data.std()
    logMsg(f"Starting bernoulli simulation with current_win_rate={current_win_rate} and current_vol={current_vol}")

    # Calculate bet size (b) and win probability (p) for Bernoulli trials
    bet_size = np.sqrt(current_win_rate**2 + current_vol**2)
    win_probability = 0.5 + (current_win_rate / (2 * bet_size))
    logMsg(f"Calculated bet_size={bet_size} and win_probability={win_probability}")

    cumulative_results = []
    for _ in range(n_simulations):
        # Simulate Bernoulli trials for n_hands based on the win probability
        wins = np.random.binomial(1, win_probability, size=n_hands)
        
        # Convert win/loss outcomes to +bet_size or -bet_size values
        outcomes = np.where(wins == 1, bet_size, -bet_size)
        
        # Calculate the cumulative profit/loss over the hands
        cumulative_sample = np.cumsum(outcomes)
        cumulative_results.append(cumulative_sample)
    
    return np.array(cumulative_results)


# run simulations
def bootstrap_simulation_normal(player_data, n_hands, n_simulations=10000,target_vol=(16.00)):

    # determine how much vol to add to player_data
    current_vol = player_data.std()
    current_win_rate = player_data.mean()

    logMsg(f'''starting normal simulation with {current_win_rate=} {current_vol=}''')

    cumulative_results = []

    for _ in range(n_simulations):

        sample = np.random.normal(current_win_rate,target_vol,size=n_hands)
        
        cumulative_sample = np.cumsum(sample)

        cumulative_results.append(cumulative_sample)

    return np.array(cumulative_results)


# Calculate statistics for each hand (cumulative)
def calculate_cumulative_stats(cumulative_results):
    mean = np.mean(cumulative_results, axis=0)
    ci_lower = np.percentile(cumulative_results, 2.5, axis=0)
    ci_upper = np.percentile(cumulative_results, 97.5, axis=0)
    return mean, ci_lower, ci_upper

# create plot of monte carlo sim
def plot_sim(data, josh_cumulative, jimmy_cumulative, challenge_end):
    
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

    # create shift for simulation versus original data
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

def runSimulation(data,challenge_end=3000,num_sims=10000,sim_type='normal'):

    logMsg(f'running sim with end={challenge_end} hands and {num_sims} sims')

    n_hands=int(challenge_end - data['Hands'].sum())

    # Run simulations for both players
    if sim_type == 'Bernoulli':
        josh_cumulative = bootstrap_simulation_bernoulli(data['Josh_profit_per_hand'], n_hands=n_hands,n_simulations=num_sims)
        jimmy_cumulative = bootstrap_simulation_bernoulli(data['Jimmy_profit_per_hand'], n_hands=n_hands,n_simulations=num_sims)
    else:   
        josh_cumulative = bootstrap_simulation_normal(data['Josh_profit_per_hand'], n_hands=n_hands,n_simulations=num_sims)
        jimmy_cumulative = bootstrap_simulation_normal(data['Jimmy_profit_per_hand'], n_hands=n_hands,n_simulations=num_sims)

    return plot_sim(data,josh_cumulative,jimmy_cumulative,challenge_end=3000)



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

def getWeather(city="63130")->str:
    """
    params:
    city - city to get weather data from
    
    returns: weather data if no error else 'Error'
    - 
    """
    def requestWeather(city="63130"):
        # Construct the URL to get the weather data from wttr.in
        url = f"http://wttr.in/{city}?nq&u?T" 
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text.strip()
                return data
            else:
                return f"Error: {response.status_code}, could not fetch weather data."
        except Exception as e:
            return f"An error occurred: {e}"


    weather_data = requestWeather(city=city)

    if weather_data.find('Error:') == -1 and weather_data.find('An error occurred:') == -1:
        # if weather_data 
        advert = weather_data.find('Follow')

        if advert != -1:
            weather_data = weather_data[:advert]    
        
        return weather_data
    else:
        # log an error here
        logMsg(weather_data)
    return 'Error'

def getBody(data:pd.DataFrame=read_csv())->str:
    
    total_hands_played = data['Cumulative Hands'].iloc[-1]
    jimmy_cumulative_winnings = data['Jimmy Cumulative Winnings'].iloc[-1]
    jimmy_profit_per_hand = jimmy_cumulative_winnings/total_hands_played
    
    josh_cumulative_winnings = data['Josh Cumulative Winnings'].iloc[-1]
    josh_pph = josh_cumulative_winnings/total_hands_played

    weatherReport = getWeather()

    # return string for email
    return (
        """Hello,\n\nI hope everyone has had a fantastic week, see below for this weekends weather forecast. I am here to provide updates on Jimmy and Josh\'s heads up challenge. """
        """Attached are the current standings and a simulation out to the end of the 3,000 hand challenge. \n\n"""
              f'Total hands played: {int(total_hands_played)} \n\n'
              f'Jimmy total = ${round(jimmy_cumulative_winnings,0)}, '
              f'Jimmy winnings/hand = ${round(jimmy_profit_per_hand,2)} \n\n'
              f'Josh total = ${round(josh_cumulative_winnings,0)}, '
              f'Josh winnings/hand = ${round(josh_pph,2)} \n\n'
              f'At the current pace it is expected that the challenge will be finished in {getTimeLeftDays(data)} days! \n\n'
              f'I hope everyone has a great week ahead. \n\n'
              f'Best,\n'
              f'JoshBot\n\n\n\n'
              "Note: This email is automated to send once weekly, please message sender to remove yourself from list.\n\n"
              f"{ weatherReport if weatherReport!= 'Error' else ' '}"
    )

# # # Testing Code
# data = read_csv()
# # print(data['Josh_profit_per_hand'])
# runSimulation(data).savefig('testfig.png')