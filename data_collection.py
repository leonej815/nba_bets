from selenium import webdriver
from selenium.webdriver.common.by import By

# class that uses Selenium to webscrape data from various sites and organizes it
class Data_Collection:
    def webDriver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)

    # method that uses the ESPN NBA scoreboard page of a particular date to scrape data
    # it is meant to be used to get the lines for the games on the given date before the games have started
    # it returns a list of dictionaries where each dictionary contains the away team, home team, away spread, home spread, and total spread
    def retrieveLineData(self, date):
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

        self.webDriver()
        self.driver.get(url)
        scoreboardEls = self.cssSelect(scoreboard_selector)

        gameDataArr = []
        for scoreboardEl in scoreboardEls:
            # skip games with fewer than 10 games played by either team
            recordEls = scoreboardEl.find_elements(By.CSS_SELECTOR, record_selector)
            awayGameCount = sum([int(x) for x in recordEls[0].text.split('-')])
            homeGameCount = sum([int(x) for x in recordEls[2].text.split('-')])
            if awayGameCount < min_game_count or homeGameCount < min_game_count:
                print('Not enough games played')
                continue

            # extract team names
            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, team_selector)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            # skip games with no betting lines
            lineEls = scoreboardEl.find_elements(By.CSS_SELECTOR, line_selector)
            if not lineEls:
                print(f'Couldn\'t find lines for {awayTeam} vs {homeTeam}')
                continue

            # extract betting line data
            favoredTeamSymbol = lineEls[0].text.split(' ')[0].lower()
            spread = lineEls[0].text.split(' ')[-1]
            total = lineEls[1].text

            # determine spread for home and away teams
            homeSpread = spread if favoredTeamSymbol == team_name_to_symbol[homeTeam] else str(float(spread) * -1)

            # compile game data
            gameData = {
                'away': awayTeam,
                'home': homeTeam,
                'away_spread': str(float(homeSpread) * -1),
                'home_spread': homeSpread,
                'total_line': total
            }
            gameDataArr.append(gameData)

        return gameDataArr

    # method goes to nba.com's advanced team stats page with last 10 games filter and returns stats for all teams
    def retrieve_stats(self):
        self.webDriver()
        stats_url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'

        heading_selector = '.Crom_container__C45Ti.crom-container .Crom_table__p1iZz .Crom_headers__mzI_m th'
        row_selector = '.Crom_body__UYOcU tr'
        value_selector = 'td'

        self.driver.get(stats_url)

        # extract table headings
        headingEls = self.cssSelect(heading_selector)
        rowEls = self.cssSelect(row_selector)

        headings = []
        for el in headingEls:
            text = el.text.lower().replace('\n', '_')
            headings.append(text)

        # extract team stats
        stats = {}
        for el in rowEls:
            valueEls = el.find_elements(By.CSS_SELECTOR, value_selector)
            teamName = valueEls[1].text.split(' ')[-1].lower()

            stats[teamName] = {}
            for i in range(6, len(valueEls) - 1):  # Skip unneeded columns
                stats[teamName][headings[i]] = valueEls[i].text

        return stats

    # retrieves the number of home games played in the last 10 games for all teams
    # returns a dictionary for all teams of the format {team name: number of home games in last 10}
    def retrieveHomeGameCounts(self):
        self.webDriver()
        url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10&Location=Home'
        row_selector = '.Crom_body__UYOcU tr'
        value_selector = 'td'

        self.driver.get(url)
        rowEls = self.cssSelect(row_selector)

        homeGameCounts = {}
        for el in rowEls:
            valueEls = el.find_elements(By.CSS_SELECTOR, value_selector)
            teamName = valueEls[1].text.split(' ')[-1].lower()
            homeGameCount = valueEls[2].text

            homeGameCounts[teamName] = homeGameCount

        return homeGameCounts

    # method goes to ESPN NBA scoredboard page for given date and retrieves the teams and scores for each
    # returns list of dictionaries [{away: away team, home: home team, away_score: away score, home_score: home score}, ...]
    def retrieveScores(self, date):
        url = f'https://www.espn.com/nba/scoreboard/_/date/{date}'
        team_selector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        score_selector = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        score_board_selector = '.Scoreboard__RowContainer'
        progress_selector = '.ScoreCell__Time'

        self.webDriver()
        self.driver.get(url)

        scoreboardEls = self.cssSelect(score_board_selector)

        scoreData = []
        for scoreboardEl in scoreboardEls:
            # skip games that are not yet finished
            gameProgress = scoreboardEl.find_element(By.CSS_SELECTOR, progress_selector).text.split('/')[0].lower()
            if gameProgress != 'final':
                continue

            # extract team names and scores
            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, team_selector)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            scoreEls = scoreboardEl.find_elements(By.CSS_SELECTOR, score_selector)
            awayScore = scoreEls[0].text
            homeScore = scoreEls[1].text

            # compile score data
            gameData = {
                'away': awayTeam,
                'home': homeTeam,
                'away_score': awayScore,
                'home_score': homeScore
            }
            scoreData.append(gameData)

        return scoreData

    # shortcut for selenium element finder by css selector
    def cssSelect(self, cssSelector):
        return self.driver.find_elements(By.CSS_SELECTOR, cssSelector)