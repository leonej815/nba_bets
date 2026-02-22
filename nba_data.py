from data_collection import Data_Collection
from data_storage import Data_Storage
from datetime import datetime, timedelta
import csv
import os
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
    line_data = data_collection.retrieve_line_data(date_today)

    if len(line_data) == 0:  # exit if no line data is available
        return

    # store the line data in the database
    data_storage = Data_Storage()
    data_storage.insert_line_data(date_today, line_data)

    # check if any games are missing stats
    stats_needed_list = data_storage.select_stats_needed()
    if len(stats_needed_list) == 0:  # exit if no stats are needed
        return

    # retrieve and store stats for games missing them
    stats = data_collection.retrieve_stats()
    data_storage.insert_stats(stats_needed_list, stats)

def update_scores():
    data_collection = Data_Collection()
    data_storage = Data_Storage()

    # find dates for games that are missing scores
    dates_for_scores = data_storage.find_dates_for_scores()
    if len(dates_for_scores) == 0:  # exit if no games need score updates
        return

    # retrieve and update scores for each date
    for date in dates_for_scores:
        game_scores_list = data_collection.retrieve_scores(date)
        data_storage.update_scores(date, game_scores_list)

def output_csv(output_directory):
    # initialize data storage and retrieve data
    data_storage = Data_Storage()
    headers = data_storage.select_headers()
    table_data = data_storage.select_all_data()
    output_path = f'{output_directory}/nba_game_data.csv'
    local_csv_path = './csv/nba_game_data.csv'

    # write data to a CSV file in the ./csv directory for local use
    with open(local_csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(table_data)
    
    # write data to the user-specified output directory
    if not os.path.samefile(output_path, local_csv_path):
        with open(output_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            csv_writer.writerows(table_data)