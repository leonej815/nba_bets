from nba_data import nba_data
import json

with open('./json/settings.json') as f:
    settings = json.loads(f.read())
csv_output_directory = settings['csv_output_directory']
nba_data(csv_output_directory)