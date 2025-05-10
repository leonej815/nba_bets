from .data_collection import Data_Collection
from .data_storage import Data_Storage
from datetime import datetime, timedelta
from .nba_criteria import Nba_Criteria
import csv
from pytz import timezone
from rich.console import Console
from rich.table import Table

def nba(csv_output_directory):
    add_pregame_data()
    update_scores()
    output_csv(csv_output_directory)

def add_pregame_data():
    tz = timezone('US/Eastern')
    today = datetime.now(tz)
    if today.hour < 4: # doing this to avoid getting stats while games are still going on at night
        today = today - timedelta(days=1)
    date_today = today.strftime('%Y%m%d')

    data_collection = Data_Collection()
    line_data = data_collection.retrieveLineData(date_today)
    if len(line_data) == 0: # no need to continue if no lines
        return
    data_storage = Data_Storage()
    data_storage.insert_line_data(date_today, line_data)

    stats_needed_list = data_storage.select_stats_needed()
    if len(stats_needed_list) == 0: # stop if no games need to have stats added
        return
    stats = data_collection.retrieve_stats()
    data_storage.insert_stats(stats_needed_list, stats)

def update_scores():
    data_collection = Data_Collection()
    data_storage = Data_Storage()

    datesForScores = data_storage.findDatesForScores()
    if len(datesForScores) == 0: # no need to continue if no games to update    
        return
    for date in datesForScores:
        gameScoresList = data_collection.retrieveScores(date)
        data_storage.updateScores(date, gameScoresList)

def output_csv(output_directory):
    dataStorage = Data_Storage()
    headers = dataStorage.selectHeaders()
    tableData = dataStorage.selectAllData()
    output_path = output_directory+'/nba_game_data.csv'

    with open('./csv/nba_game_data.csv', 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(headers)
        csvWriter.writerows(tableData)

    with open(output_path, 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(headers)
        csvWriter.writerows(tableData)

# def console_output:
    # ds = Data_Storage()
    # betting_data = ds.select_betting_data()
    # nbaCriteria = Nba_Criteria()
    # console = Console()
    # table = Table(title='NBA Picks') 
    # headers = ['away', 'home', 'home spread', 'total line', 'ppg total pick', 'ts%, reb%, tov% spread pick', 'pace, ortg spread pick', 'opp drtg, pace spread pick', 'avg pace, ortg, drtg spread pick']
    # for header in headers:
    #     table.add_column(header)
    # for game_data in betting_data:
    #     row = [game_data['away'], game_data['home'], str(game_data['home_spread']), str(game_data['total_line'])]
    #     row.append(nbaCriteria.get_ppg_total_pick(game_data))
    #     row.append(nbaCriteria.get_ts_reb_tov_spread_pick(game_data))
    #     row.append(nbaCriteria.get_ppg_spread_pick(game_data))
    #     row.append(nbaCriteria.get_drtg_pace_spread_pick(game_data))
    #     row.append(nbaCriteria.get_avg_pace_ortg_drtg_spread_pick(game_data))
    #     table.add_row(*row)
    # console.print(table)