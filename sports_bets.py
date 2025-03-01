from nba.nba_bets import nba
from nfl.nfl_bets import nfl
import json

with open('./json/settings.json') as f:
    settings = json.loads(f.read())
csv_output_directory = settings['csv_output_directory']
nba_on = settings['nba']
nfl_on = settings['nfl']
if nba_on == True:
    nba(csv_output_directory)
if nfl_on == True:
    nfl(csv_output_directory)