from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime

class Data_Collection:
    def webDriver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)           


    def retrieveLineData(self, date): #date format: yyyymmdd
        TEAM_NAME_TO_SYMBOL = {'orioles':'bal','red sox':'bos','yankees':'nyy','rays':'tb','blue jays':'tor','white sox':'chw','guardians':'cle','tigers':'det','royals':'kc','twins':'min','astros':'hou','angels':'laa','athletics':'oak','mariners':'sea','rangers':'tex','braves':'atl','marlins':'mia','mets':'nym','phillies':'phi','nationals':'wsh','cubs':'chc','reds':'cin','brewers':'mil','pirates':'pit','cardinals':'stl','diamondbacks':'ari','rockies':'col','dodgers':'lad','padres':'sd','giants':'sf'}
        MIN_GAME_COUNT = 10
        URL = 'https://www.espn.com/mlb/scoreboard/_/date/' + date
        SCOREBOARD_SELECTOR = '.Scoreboard__RowContainer'
        TEAM_SELECTOR = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        LINE_SELECTOR = '.VZTD.mLASH.rIczU.LNzKp.jsU.hfDkF.FoYYc.FuEs' # selects both spreads and totals
        RECORD_SELECTOR = '.ScoreboardScoreCell__Record' # selects both record and home/away based record

        self.webDriver()
        self.driver.get(URL)
        scoreboardEls = self.cssSelect(SCOREBOARD_SELECTOR)

        gameDataArr = []
        for scoreboardEl in scoreboardEls:
            # the following is to check if there was less than 10 games played
            recordEls = scoreboardEl.find_elements(By.CSS_SELECTOR, RECORD_SELECTOR)
            awayGameCount = sum([int(x) for x in recordEls[0].text.split('-')])
            homeGameCount = sum([int(x) for x in recordEls[2].text.split('-')])
            if(awayGameCount < MIN_GAME_COUNT or homeGameCount < MIN_GAME_COUNT): #skip if not enough games
                continue

            lineEls = scoreboardEl.find_elements(By.CSS_SELECTOR, LINE_SELECTOR)
            
            if not lineEls: # if no lines skip to next game scoreboard
                continue

            favoredTeamSymbol = lineEls[0].text.split(' ')[0].lower()
            spread = lineEls[0].text.split(' ')[-1]
            total = lineEls[1].text

            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, TEAM_SELECTOR)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            if favoredTeamSymbol == TEAM_NAME_TO_SYMBOL[homeTeam]:
                homeSpread = spread
            else:
                homeSpread = str(float(spread) * -1)

            gameData = {}
            gameData['away'] = awayTeam
            gameData['home'] = homeTeam
            gameData['away_spread'] = str(float(homeSpread) * -1)
            gameData['home_spread'] = homeSpread
            gameData['total_line'] = total
            gameDataArr.append(gameData)

        return gameDataArr

    def retrieve_stats(self):
        self.webDriver()
        STATS_URL = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'

        HEADING_SELECTOR = '.Crom_container__C45Ti.crom-container .Crom_table__p1iZz .Crom_headers__mzI_m th'
        ROW_SELECTOR = '.Crom_body__UYOcU tr'
        VALUE_SELECTOR = 'td'
 
        self.driver.get(STATS_URL)

        headingEls = self.cssSelect(HEADING_SELECTOR)
        rowEls = self.cssSelect(ROW_SELECTOR) 

        headings = []
        for el in headingEls:
            text = el.text.lower()
            if ('\n' in el.text):
                text = text.replace('\n', '_')

            headings.append(text)
 
        stats = {}
        for el in rowEls:
            valueEls = el.find_elements(By.CSS_SELECTOR, VALUE_SELECTOR)
            teamName = valueEls[1].text.split(' ')[-1].lower()

            stats[teamName] = {}
            for i in range(6, len(valueEls)-1): # skip unneeded columns
                stats[teamName][headings[i]] = valueEls[i].text

        return stats

    def retrieveScores(self, date): #date format is 'yyyymmdd'
        URL = 'https://www.espn.com/mlb/scoreboard/_/date/' + date
        TEAM_SELECTOR = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        SCORE_SELECTOR = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        SCOREBOARD_SELECTOR = '.Scoreboard__RowContainer'
        PROGRESS_SELECTOR = '.ScoreCell__Time'

        self.webDriver()
        self.driver.get(URL)

        scoreboardEls = self.cssSelect(SCOREBOARD_SELECTOR)
    
        scoreData = []
        for scoreboardEl in scoreboardEls:
            # the following checks if the game is finished before collecting the scores
            gameProgress = scoreboardEl.find_element(By.CSS_SELECTOR, PROGRESS_SELECTOR).text.split('/')[0].lower()
            if(gameProgress != 'final'):
                continue

            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, TEAM_SELECTOR)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            scoreEls = scoreboardEl.find_elements(By.CSS_SELECTOR, SCORE_SELECTOR)
            awayScore = scoreEls[0].text
            homeScore = scoreEls[1].text

            gameData = {}
            gameData['away'] = awayTeam
            gameData['home'] = homeTeam
            gameData['away_score'] = awayScore
            gameData['home_score'] = homeScore
            scoreData.append(gameData)

        return scoreData


    def cssSelect(self, cssSelector):
        return self.driver.find_elements(By.CSS_SELECTOR, cssSelector)







        



        
