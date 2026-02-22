from selenium import webdriver
from selenium.webdriver.common.by import By

# class that uses Selenium to webscrape data from various sites and organizes it
class Data_Collection:
    def web_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)

    # method that uses the ESPN NBA scoreboard page of a particular date to scrape data
    # it is meant to be used to get the lines for the games on the given date before the games have started
    # it returns a list of dictionaries where each dictionary contains the away team, home team, away spread, home spread, and total spread
    def retrieve_line_data(self, date):
        team_name_to_symbol = {
            'celtics':'bos', 'warriors':'gs', 'cavaliers':'cle', 'grizzlies':'mem', 'nets':'bkn', 'lakers':'lal',
            'hawks':'atl', 'kings':'sac', 'bulls':'chi', 'nuggets':'den', 'magic':'orl', 'thunder':'okc',
            'bucks':'mil', 'suns':'phx', 'mavericks':'dal', 'wizards':'wsh', 'knicks':'ny', 'hornets':'cha',
            'raptors':'tor', 'timberwolves':'min', 'clippers':'lac', '76ers':'phi', 'rockets':'hou', 'pacers':'ind',
            'pelicans':'no', 'blazers':'por', 'pistons':'det', 'spurs':'sa', 'heat':'mia', 'jazz':'utah'
        }
        min_game_count = 10
        url = f'https://www.espn.com/nba/scoreboard/_/date/{date}'
        scoreboard_selector = '.Scoreboard__RowContainer'
        team_selector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        line_selector = '.rIczU.iygLn'
        record_selector = '.ScoreboardScoreCell__Record'

        self.web_driver()
        self.driver.get(url)
        scoreboard_els = self.css_select(scoreboard_selector)

        game_data_arr = []
        for scoreboard_el in scoreboard_els:
            # skip games with fewer than 10 games played by either team
            record_els = scoreboard_el.find_elements(By.CSS_SELECTOR, record_selector)
            away_game_count = sum([int(x) for x in record_els[0].text.split('-')])
            home_game_count = sum([int(x) for x in record_els[2].text.split('-')])
            if away_game_count < min_game_count or home_game_count < min_game_count:
                print('Not enough games played')
                continue

            # extract team names
            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            # skip games with no betting lines
            line_els = scoreboard_el.find_elements(By.CSS_SELECTOR, line_selector)
            if not line_els:
                print(f'Couldn\'t find lines for {away_team} at {home_team}')
                continue

            # extract betting line data
            favored_team_symbol = line_els[0].text.split(' ')[0].lower()
            spread = line_els[0].text.split(' ')[-1]
            total = line_els[1].text

            # determine spread for home and away teams
            home_spread = spread if favored_team_symbol == team_name_to_symbol[home_team] else str(float(spread) * -1)

            # compile game data
            game_data = {
                'away': away_team,
                'home': home_team,
                'away_spread': str(float(home_spread) * -1),
                'home_spread': home_spread,
                'total_line': total
            }
            game_data_arr.append(game_data)

        return game_data_arr

    # method goes to nba.com's advanced team stats page with last 10 games filter and returns stats for all teams
    def retrieve_stats(self):
        self.web_driver()
        stats_url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'

        heading_selector = '.Crom_container__C45Ti.crom-container .Crom_table__p1iZz .Crom_headers__mzI_m th'
        row_selector = '.Crom_body__UYOcU tr'
        value_selector = 'td'

        self.driver.get(stats_url)

        # extract table headings
        heading_els = self.css_select(heading_selector)
        row_els = self.css_select(row_selector)

        headings = []
        for el in heading_els:
            text = el.text.lower().replace('\n', '_')
            headings.append(text)

        # extract team stats
        stats = {}
        for el in row_els:
            value_els = el.find_elements(By.CSS_SELECTOR, value_selector)
            team_name = value_els[1].text.split(' ')[-1].lower()

            stats[team_name] = {}
            for i in range(6, len(value_els) - 1):  # Skip unneeded columns
                stats[team_name][headings[i]] = value_els[i].text

        return stats

    # retrieves the number of home games played in the last 10 games for all teams
    # returns a dictionary for all teams of the format {team name: number of home games in last 10}
    def retrievehome_game_counts(self):
        self.web_driver()
        url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10&Location=Home'
        row_selector = '.Crom_body__UYOcU tr'
        value_selector = 'td'

        self.driver.get(url)
        row_els = self.css_select(row_selector)

        home_game_counts = {}
        for el in row_els:
            value_els = el.find_elements(By.CSS_SELECTOR, value_selector)
            team_name = value_els[1].text.split(' ')[-1].lower()
            home_game_count = value_els[2].text

            home_game_counts[team_name] = home_game_count

        return home_game_counts

    # method goes to ESPN NBA scoredboard page for given date and retrieves the teams and scores for each
    # returns list of dictionaries [{away: away team, home: home team, away_score: away score, home_score: home score}, ...]
    def retrieve_scores(self, date):
        url = f'https://www.espn.com/nba/scoreboard/_/date/{date}'
        team_selector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        score_selector = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        score_board_selector = '.Scoreboard__RowContainer'
        progress_selector = '.ScoreCell__Time'

        self.web_driver()
        self.driver.get(url)

        scoreboard_els = self.css_select(score_board_selector)

        score_data = []
        for scoreboard_el in scoreboard_els:
            # skip games that are not yet finished
            game_progress = scoreboard_el.find_element(By.CSS_SELECTOR, progress_selector).text.split('/')[0].lower()
            if game_progress != 'final':
                continue

            # extract team names and scores
            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            score_els = scoreboard_el.find_elements(By.CSS_SELECTOR, score_selector)
            away_score = score_els[0].text
            home_score = score_els[1].text

            # compile score data
            game_data = {
                'away': away_team,
                'home': home_team,
                'away_score': away_score,
                'home_score': home_score
            }
            score_data.append(game_data)

        return score_data

    # shortcut for selenium element finder by css selector
    def css_select(self, css_selector):
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)