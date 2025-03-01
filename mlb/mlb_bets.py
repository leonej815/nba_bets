from .data_collection import Data_Collection
from .data_storage import Data_Storage
from datetime import datetime
import csv
import json

def nfl(csv_output_directory):
    add_pregame_data()
    update_scores()
    output_csv(csv_output_directory)

def add_pregame_data():
    data_collection = Data_Collection()
    week_year = data_collection.get_week_year()
    week = week_year['week']
    year = week_year['year']
    line_data = data_collection.getLineData(year, week)
    if len(line_data) == 0:
        return
    data_storage = Data_Storage()
    data_storage.insert_line_data(year, week, line_data)
    stats_needed_list = data_storage.select_stats_needed()
    if len(stats_needed_list) == 0:
        return
    stats = data_collection.getStats(year, week)
    data_storage.insert_stats(stats_needed_list, stats)

def update_scores():
    dc = Data_Collection()
    ds = Data_Storage()

    year_week_list = ds.findYearWeekForUpdate()
    if len(year_week_list) == 0: # end if nothing to update
        return
    for year_week in year_week_list:
        year = year_week['year']
        week = year_week['week']
        
        game_scores_list = dc.retrieveScores(year, week)
        ds.updateScores(year, week, game_scores_list)

def output_csv(output_directory):
    data_storage = Data_Storage()
    headers = data_storage.selectHeaders()
    table_data = data_storage.selectAllData()
    output_path = output_directory + '/nfl_game_data.csv'

    with open(output_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(table_data)       

    with open('./csv/nfl_game_data.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(table_data)