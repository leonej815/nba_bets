from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime

class Data_Collection:
    """
    A class for collecting NBA-related data from web sources using Selenium.
    """

    def webDriver(self):
        """
        Initializes the Selenium WebDriver with specified Chrome options.
        """
        options = webdriver.ChromeOptions()
        # Uncomment the next line to run the scraper in headless mode
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)

    def retrieveLineData(self, date):
        """
        Retrieves NBA betting line data for a specific date from ESPN.

        Args:
            date (str): The date in 'yyyymmdd' format.

        Returns:
            list: A list of dictionaries containing game data.
        """
        TEAM_NAME_TO_SYMBOL = {
            'celtics':'bos', 'warriors':'gs', 'cavaliers':'cle', 'grizzlies':'mem', 'nets':'bkn', 'lakers':'lal',
            'hawks':'atl', 'kings':'sac', 'bulls':'chi', 'nuggets':'den', 'magic':'orl', 'thunder':'okc',
            'bucks':'mil', 'suns':'phx', 'mavericks':'dal', 'wizards':'wsh', 'knicks':'ny', 'hornets':'cha',
            'raptors':'tor', 'timberwolves':'min', 'clippers':'lac', '76ers':'phi', 'rockets':'hou', 'pacers':'ind',
            'pelicans':'no', 'blazers':'por', 'pistons':'det', 'spurs':'sa', 'heat':'mia', 'jazz':'utah'
        }
        MIN_GAME_COUNT = 10
        URL = f'https://www.espn.com/nba/scoreboard/_/date/{date}'
        SCOREBOARD_SELECTOR = '.Scoreboard__RowContainer'
        TEAM_SELECTOR = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        LINE_SELECTOR = '.VZTD.mLASH.rIczU.LNzKp.jsU.hfDkF.FoYYc.FuEs'
        RECORD_SELECTOR = '.ScoreboardScoreCell__Record'

        self.webDriver()
        self.driver.get(URL)
        scoreboardEls = self.cssSelect(SCOREBOARD_SELECTOR)

        gameDataArr = []
        for scoreboardEl in scoreboardEls:
            # Skip games with fewer than 10 games played by either team
            recordEls = scoreboardEl.find_elements(By.CSS_SELECTOR, RECORD_SELECTOR)
            awayGameCount = sum([int(x) for x in recordEls[0].text.split('-')])
            homeGameCount = sum([int(x) for x in recordEls[2].text.split('-')])
            if awayGameCount < MIN_GAME_COUNT or homeGameCount < MIN_GAME_COUNT:
                continue

            # Skip games with no betting lines
            lineEls = scoreboardEl.find_elements(By.CSS_SELECTOR, LINE_SELECTOR)
            if not lineEls:
                continue

            # Extract betting line data
            favoredTeamSymbol = lineEls[0].text.split(' ')[0].lower()
            spread = lineEls[0].text.split(' ')[-1]
            total = lineEls[1].text

            # Extract team names
            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, TEAM_SELECTOR)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            # Determine spread for home and away teams
            homeSpread = spread if favoredTeamSymbol == TEAM_NAME_TO_SYMBOL[homeTeam] else str(float(spread) * -1)

            # Compile game data
            gameData = {
                'away': awayTeam,
                'home': homeTeam,
                'away_spread': str(float(homeSpread) * -1),
                'home_spread': homeSpread,
                'total_line': total
            }
            gameDataArr.append(gameData)

        return gameDataArr

    def retrieve_stats(self):
        """
        Retrieves advanced NBA team stats for the last 10 games from NBA.com.

        Returns:
            dict: A dictionary of stats keyed by team name.
        """
        self.webDriver()
        STATS_URL = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'

        HEADING_SELECTOR = '.Crom_container__C45Ti.crom-container .Crom_table__p1iZz .Crom_headers__mzI_m th'
        ROW_SELECTOR = '.Crom_body__UYOcU tr'
        VALUE_SELECTOR = 'td'

        self.driver.get(STATS_URL)

        # Extract table headings
        headingEls = self.cssSelect(HEADING_SELECTOR)
        rowEls = self.cssSelect(ROW_SELECTOR)

        headings = []
        for el in headingEls:
            text = el.text.lower().replace('\n', '_')
            headings.append(text)

        # Extract team stats
        stats = {}
        for el in rowEls:
            valueEls = el.find_elements(By.CSS_SELECTOR, VALUE_SELECTOR)
            teamName = valueEls[1].text.split(' ')[-1].lower()

            stats[teamName] = {}
            for i in range(6, len(valueEls) - 1):  # Skip unneeded columns
                stats[teamName][headings[i]] = valueEls[i].text

        return stats

    def retrieveHomeGameCounts(self):
        """
        Retrieves the number of home games played by each NBA team in the last 10 games.

        Returns:
            dict: A dictionary mapping team names to their home game counts.
        """
        self.webDriver()
        URL = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10&Location=Home'
        ROW_SELECTOR = '.Crom_body__UYOcU tr'
        VALUE_SELECTOR = 'td'

        self.driver.get(URL)
        rowEls = self.cssSelect(ROW_SELECTOR)

        homeGameCounts = {}
        for el in rowEls:
            valueEls = el.find_elements(By.CSS_SELECTOR, VALUE_SELECTOR)
            teamName = valueEls[1].text.split(' ')[-1].lower()
            homeGameCount = valueEls[2].text

            homeGameCounts[teamName] = homeGameCount

        return homeGameCounts

    def retrieveScores(self, date):
        """
        Retrieves final scores for NBA games played on a specific date.

        Args:
            date (str): The date in 'yyyymmdd' format.

        Returns:
            list: A list of dictionaries containing game score data.
        """
        URL = f'https://www.espn.com/nba/scoreboard/_/date/{date}'
        TEAM_SELECTOR = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        SCORE_SELECTOR = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        SCOREBOARD_SELECTOR = '.Scoreboard__RowContainer'
        PROGRESS_SELECTOR = '.ScoreCell__Time'

        self.webDriver()
        self.driver.get(URL)

        scoreboardEls = self.cssSelect(SCOREBOARD_SELECTOR)

        scoreData = []
        for scoreboardEl in scoreboardEls:
            # Skip games that are not yet finished
            gameProgress = scoreboardEl.find_element(By.CSS_SELECTOR, PROGRESS_SELECTOR).text.split('/')[0].lower()
            if gameProgress != 'final':
                continue

            # Extract team names and scores
            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, TEAM_SELECTOR)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            scoreEls = scoreboardEl.find_elements(By.CSS_SELECTOR, SCORE_SELECTOR)
            awayScore = scoreEls[0].text
            homeScore = scoreEls[1].text

            # Compile score data
            gameData = {
                'away': awayTeam,
                'home': homeTeam,
                'away_score': awayScore,
                'home_score': homeScore
            }
            scoreData.append(gameData)

        return scoreData

    def cssSelect(self, cssSelector):
        """
        Finds elements using a CSS selector.

        Args:
            cssSelector (str): The CSS selector to use.

        Returns:
            list: A list of Selenium WebElement objects matching the selector.
        """
        return self.driver.find_elements(By.CSS_SELECTOR, cssSelector)