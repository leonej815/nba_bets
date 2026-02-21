from data_collection import Data_Collection
from data_storage import Data_Storage
from datetime import datetime, timedelta
import csv
from pytz import timezone

# function to add games that haven't started yet to database
# adds scores to 
def nba_data(csv_output_directory):
    add_pregame_data()
    update_scores()
    output_csv(csv_output_directory)

def add_pregame_data():
    # set timezone to US/Eastern and adjust for games played late at night
    tz = timezone('US/Eastern')
    today = datetime.now(tz)
    if today.hour < 4:  # avoid collecting stats while games are still in progress
        today = today - timedelta(days=1)
    date_today = today.strftime('%Y%m%d')

    # initialize data collection and fetch line data
    data_collection = Data_Collection()
    line_data = data_collection.retrieveLineData(date_today)

    if len(line_data) == 0:  # Exit if no line data is available
        return

    # Store the line data in the database
    data_storage = Data_Storage()
    data_storage.insert_line_data(date_today, line_data)

    # Check if any games are missing stats
    stats_needed_list = data_storage.select_stats_needed()
    if len(stats_needed_list) == 0:  # Exit if no stats are needed
        return

    # Retrieve and store stats for games missing them
    stats = data_collection.retrieve_stats()
    data_storage.insert_stats(stats_needed_list, stats)

def update_scores():
    # Initialize data collection and storage
    data_collection = Data_Collection()
    data_storage = Data_Storage()

    # Find dates for games that are missing scores
    datesForScores = data_storage.findDatesForScores()
    if len(datesForScores) == 0:  # Exit if no games need score updates
        return

    # Retrieve and update scores for each date
    for date in datesForScores:
        gameScoresList = data_collection.retrieveScores(date)
        data_storage.updateScores(date, gameScoresList)

def output_csv(output_directory):
    # Initialize data storage and retrieve data
    dataStorage = Data_Storage()
    headers = dataStorage.selectHeaders()
    tableData = dataStorage.selectAllData()
    output_path = f'{output_directory}/nba_game_data.csv'

    # Write data to a CSV file in the ./csv directory for local use
    with open('./csv/nba_game_data.csv', 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(headers)
        csvWriter.writerows(tableData)

    # Write data to the user-specified output directory
    with open(output_path, 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(headers)
        csvWriter.writerows(tableData)