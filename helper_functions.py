from datetime import datetime
import pandas as pd


def logMsg(message):
    current_time = datetime.now().time()
    with open('heads_up_log.txt', 'a') as file:
        file.write(f'{current_time}:\t{message}\n')

# Function to read Excel 
def read_csv() -> pd.DataFrame:
    # Load the Excel file
    file_path = "HeadsUpData.csv"
    data = pd.read_csv(file_path)
    data.dropna(inplace=True)

    # Calculate metrics required for other aspects of the code
    data['Cumulative Hands'] = data['Hands'].cumsum()
    data['Josh_profit_per_hand'] = data['Ending total josh'] / data['Hands']
    data['Jimmy_profit_per_hand'] = data['Ending total jimmy'] / data['Hands']
    data['Josh Cumulative Winnings'] = data['Ending total josh'].cumsum()
    data['Jimmy Cumulative Winnings'] = data['Ending total jimmy'].cumsum()

    return data