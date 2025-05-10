from data_collection import Data_Collection
from data_storage import Data_Storage
from datetime import datetime, timedelta
from nba_criteria import Nba_Criteria
import csv
from pytz import timezone

def nba_data(csv_output_directory):
    """
    Orchestrates the workflow for collecting, storing, and exporting NBA data.

    Args:
        csv_output_directory (str): The directory where the output CSV file will be saved.
    """
    add_pregame_data()
    update_scores()
    output_csv(csv_output_directory)

def add_pregame_data():
    """
    Collects and stores pregame data, including lines and stats, for today's games.
    """
    # Set timezone to US/Eastern and adjust for games played late at night
    tz = timezone('US/Eastern')
    today = datetime.now(tz)
    if today.hour < 4:  # Avoid collecting stats while games are still in progress
        today = today - timedelta(days=1)
    date_today = today.strftime('%Y%m%d')

    # Initialize data collection and fetch line data
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
    """
    Updates scores for games that are marked as incomplete in the database.
    """
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
    """
    Exports all NBA game data from the database into a CSV file.

    Args:
        output_directory (str): The directory where the output CSV file will be saved.
    """
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