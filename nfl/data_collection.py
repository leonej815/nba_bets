from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import math
from bs4 import BeautifulSoup
import requests

class Data_Collection:
    def webDriver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)
        self.lastNGames = 4


    def get_week_year(self):
        url = 'https://www.espn.com/nfl/scoreboard'
        self.webDriver()
        self.driver.get(url)

        yearElSelector = '.custom--week.is-active a'
        yearEl = self.driver.find_element(By.CSS_SELECTOR, yearElSelector) 
        year = yearEl.get_attribute('href').split('/')[-3]    
        
        weekElSelector = '.custom--week.is-active span'
        weekEl = self.driver.find_element(By.CSS_SELECTOR, weekElSelector)
        week = weekEl.text.split(' ')[-1]

        data = {}
        data['year'] = year
        data['week'] = week
        return data


    def getLineData(self, year, week):
        url = 'https://www.espn.com/nfl/scoreboard/_/week/' + week + '/year/' + year
        self.webDriver()
        self.driver.get(url)

        scoreboardElsSelector = '.Scoreboard__RowContainer'
        scoreboardEls = self.driver.find_elements(By.CSS_SELECTOR, scoreboardElsSelector)
        gameDataArr = []
        for scoreboardEl in scoreboardEls:
            recordElsSelector = '.ScoreboardScoreCell__Record' # selects both overall record and home/away based record
            recordEls = scoreboardEl.find_elements(By.CSS_SELECTOR, recordElsSelector)
            if len(recordEls) < 3: # skip if no home and away record when games played in other countries
                continue

            awayGameCount = sum([int(x) for x in recordEls[0].text.split('-')])
            homeGameCount = sum([int(x) for x in recordEls[2].text.split('-')])

            minGameCount = 4
            if(awayGameCount < minGameCount or homeGameCount < minGameCount): #skip if not enough games
                continue

            lineElsSelector = '.VZTD.mLASH.rIczU.LNzKp.jsU.hfDkF.FoYYc.FuEs' # selects both spreads and totals
            lineEls = scoreboardEl.find_elements(By.CSS_SELECTOR, lineElsSelector)           
            if not lineEls: # if no lines (game started already) skip to next game scoreboard
                continue

            favoredTeamSymbol = lineEls[0].text.split(' ')[0].lower()
            spread = lineEls[0].text.split(' ')[-1]
            if(spread == 'OFF'):
                continue
            total = lineEls[1].text

            teamElsSelector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
            teamEls = scoreboardEl.find_elements(By.CSS_SELECTOR, teamElsSelector)
            awayTeam = teamEls[0].text.split(' ')[-1].lower()
            homeTeam = teamEls[1].text.split(' ')[-1].lower()

            teamNameToSymbol = {'bills':'buf','jets':'nyj','dolphins':'mia','patriots':'ne','steelers':'pit','ravens':'bal','bengals':'cin','browns':'cle','texans':'hou','colts':'ind','jaguars':'jax','titans':'ten','chiefs':'kc','broncos':'den','chargers':'lac','raiders':'lv','commanders':'wsh','eagles':'phi','cowboys':'dal','giants':'nyg','lions':'det','packers':'gb','vikings':'min','bears':'chi','falcons':'atl','buccaneers':'tb','saints':'no','panthers':'car','cardinals':'ari','49ers':'sf','seahawks':'sea','rams':'lar'}
            if favoredTeamSymbol == teamNameToSymbol[homeTeam]:
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


    def getStats(self, year, week):
        proFbRefSymbols = ['buf','mia','nwe','nyj','pit','rav','cin','cle','htx','clt','jax','oti','kan','den','sdg','rai','was','phi','dal','nyg','atl','tam','nor','car','det','gnb','min','chi','crd','sea','sfo','ram']
        self.webDriver()
        statsData = {}
        for teamSymbol in proFbRefSymbols:
            url = 'https://www.pro-football-reference.com/teams/' + teamSymbol + '/' + year + '/gamelog/'
            self.driver.get(url)

            teamNameElSelector = 'div[data-template="Partials/Teams/Summary"] h1 span'
            teamName = self.driver.find_elements(By.CSS_SELECTOR, teamNameElSelector)[1].text.split(' ')[-1].lower()

            tableElSelector = '#gamelog2024'
            keys = ['location','opponent','tm','opp','cmp','p_att','p_yds','p_td','int','sk','sk_yds','p_y/a','ny/a','cmp%','rate','r_att','r_yds','r_y/a','r_td','fgm','fga','xpm','xpa','pnt','pnt_yds','3dconv','3datt','4dconv','4datt','top']            
            teamLogData = self._getGameLogStats(tableElSelector, keys)
            oppTableElSelector = '#gamelog_opp2024'
            oppKeys = ['location','opponent','tm','opp','opp_cmp','opp_p_att','opp_p_yds','opp_p_td','opp_int','opp_sk','opp_sk_yds','opp_p_y/a','opp_ny/a','opp_cmp%','opp_rate','opp_r_att','opp_r_yds','opp_r_y/a','opp_r_td','opp_fgm','opp_fga','opp_xpm','opp_xpa','opp_pnt','opp_pnt_yds','opp_3dconv','opp_3datt','opp_4dconv','opp_4datt','opp_top']
            oppLogData = self._getGameLogStats(oppTableElSelector, oppKeys)
            if teamLogData == None or oppLogData == None: # skip this team if there weren't enough games worth of stats
                continue
            teamStats = {}
            awayGameCount = 0
            for location in teamLogData['location']:
                if location == '@':
                    awayGameCount += 1
            homeGameCount = self.lastNGames - awayGameCount
            teamStats['away_game_count'] = awayGameCount
            teamStats['home_game_count'] = homeGameCount
            teamStats['ppg'] = sum(teamLogData['tm']) / self.lastNGames   
            teamStats['pass_comp_pg'] = sum(teamLogData['cmp']) / self.lastNGames
            teamStats['pass_att_pg'] = sum(teamLogData['p_att']) / self.lastNGames
            teamStats['pass_yd_pg'] = sum(teamLogData['p_yds']) / self.lastNGames
            teamStats['pass_td_pg'] = sum(teamLogData['p_td']) / self.lastNGames
            teamStats['int_thrown_pg'] = sum(teamLogData['int']) / self.lastNGames
            teamStats['sacks_taken_pg'] = sum(teamLogData['sk']) / self.lastNGames
            teamStats['rush_att_pg'] = sum(teamLogData['r_att']) / self.lastNGames
            teamStats['rush_yds_pg'] = sum(teamLogData['r_yds']) / self.lastNGames
            teamStats['rush_td_pg'] = sum(teamLogData['r_td']) / self.lastNGames
            teamStats['fgm_pg'] = sum(teamLogData['fgm']) / self.lastNGames
            teamStats['fga_pg'] = sum(teamLogData['fga']) / self.lastNGames
            teamStats['pnt_pg'] = sum(teamLogData['pnt']) / self.lastNGames
            teamStats['3d_conv_pg'] = sum(teamLogData['3dconv']) / self.lastNGames
            teamStats['3d_att_pg'] = sum(teamLogData['3datt']) / self.lastNGames
            teamStats['4d_conv_pg'] = sum(teamLogData['4dconv']) / self.lastNGames
            teamStats['4d_att_pg'] = sum(teamLogData['4datt']) / self.lastNGames
            topSum = 0
            for top in teamLogData['top']:
                seconds = int(top.split(':')[-1])/60
                minutes = int(top.split(':')[0]) + seconds
                topSum += minutes
            teamStats['top'] = round(topSum / self.lastNGames, 2)
         
            teamStats['opp_ppg'] = sum(oppLogData['opp']) / self.lastNGames
            teamStats['opp_pass_comp_pg'] = sum(oppLogData['opp_cmp']) / self.lastNGames
            teamStats['opp_pass_att_pg'] = sum(oppLogData['opp_p_att']) / self.lastNGames
            teamStats['opp_pass_yd_pg'] = sum(oppLogData['opp_p_yds']) / self.lastNGames
            teamStats['opp_pass_td_pg'] = sum(oppLogData['opp_p_td']) / self.lastNGames
            teamStats['opp_int_thrown_pg'] = sum(oppLogData['opp_int']) / self.lastNGames
            teamStats['opp_sacks_taken_pg'] = sum(oppLogData['opp_sk']) / self.lastNGames
            teamStats['opp_rush_att_pg'] = sum(oppLogData['opp_r_att']) / self.lastNGames
            teamStats['opp_rush_yds_pg'] = sum(oppLogData['opp_r_yds']) / self.lastNGames
            teamStats['opp_rush_td_pg'] = sum(oppLogData['opp_r_td']) / self.lastNGames
            teamStats['opp_fgm_pg'] = sum(oppLogData['opp_fgm']) / self.lastNGames
            teamStats['opp_fga_pg'] = sum(oppLogData['opp_fga']) / self.lastNGames
            teamStats['opp_pnt_pg'] = sum(oppLogData['opp_pnt']) / self.lastNGames
            teamStats['opp_3d_conv_pg'] = sum(oppLogData['opp_3dconv']) / self.lastNGames
            teamStats['opp_3d_att_pg'] = sum(oppLogData['opp_3datt']) / self.lastNGames
            teamStats['opp_4d_conv_pg'] = sum(oppLogData['opp_4dconv']) / self.lastNGames
            teamStats['opp_4d_att_pg'] = sum(oppLogData['opp_4datt']) / self.lastNGames
            oppTopSum = 0
            for top in oppLogData['opp_top']:
                seconds = int(top.split(':')[-1])/60
                minutes = int(top.split(':')[0]) + seconds
                oppTopSum += minutes
            teamStats['opp_top'] = round(oppTopSum / self.lastNGames, 2)

            statsData[teamName] = teamStats

        return statsData


    def _getGameLogStats(self, gameLogTableElSelector, keys): # helper function so I don't have to duplicate code for team and opponent     
        gameLogTableEl = self.driver.find_element(By.CSS_SELECTOR, gameLogTableElSelector)
        gameLogTableRowEls = gameLogTableEl.find_elements(By.CSS_SELECTOR, 'tr')[2:] # remove first two rows with no game logs
        gameLogTableRowEls.reverse() # reverse so I can stop after having data from last 4 game logs

        gameLogData = {}
        for key in keys:
            gameLogData[key] = []

        logCount = 0
        for rowEl in gameLogTableRowEls:
            outcomeElSelector = 'td[data-stat="game_outcome"]'
            outcome = rowEl.find_element(By.CSS_SELECTOR, outcomeElSelector).text.lower()
            if outcome != 'w' and outcome != 'l': # skip log if there is no game outcome
                continue

            logValueEls = rowEl.find_elements(By.CSS_SELECTOR, 'td')[5:] # remove rows without stats
            for i in range(len(logValueEls)):
                if(keys[i] == 'top' or keys[i] == 'opp_top' or keys[i] == 'location' or keys[i] == 'opponent'):
                    gameLogData[keys[i]].append(logValueEls[i].text)
                else:
                    gameLogData[keys[i]].append(float(logValueEls[i].text))
            
            logCount +=1
            if logCount == self.lastNGames:
                break

        if logCount != self.lastNGames: # return None if not enough game so I can't inerst stats in the database later
            return None

        return gameLogData


    def retrieveScores(self, year, week): #date format is 'yyyymmdd'
        URL = 'https://www.espn.com/nfl/scoreboard/_/week/' + week + '/year/' + year
        TEAM_SELECTOR = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        SCORE_SELECTOR = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        SCOREBOARD_SELECTOR = '.Scoreboard__RowContainer'
        PROGRESS_SELECTOR = '.ScoreCell__Time'

        self.webDriver()
        self.driver.get(URL)

        scoreboardEls = self.driver.find_elements(By.CSS_SELECTOR, SCOREBOARD_SELECTOR)
    
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






        



        
