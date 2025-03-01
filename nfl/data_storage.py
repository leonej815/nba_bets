import sqlite3

class Data_Storage:
    def __init__(self):
        self.conn = sqlite3.connect('./sqlite/sports_bets.sqlite')
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS nfl_game_data(id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER, week INTEGER, away TEXT, home TEXT, away_spread REAL, home_spread REAL, total_line REAL, away_score INTEGER, home_score INTEGER,
        
        away_home_game_count INTEGER, away_away_game_count INTEGER, 
        
        away_ppg REAL, away_pass_comp_pg REAL, away_pass_yd_pg REAL, away_pass_td_pg REAL, away_int_thrown_pg REAL, away_sacks_taken_pg REAL, away_rush_att_pg REAL, away_rush_yds_pg REAL, away_rush_td_pg REAL, away_fgm_pg REAL, away_fga_pg REAL, away_pnt_pg REAL, away_3d_conv_pg REAL, away_3d_att_pg REAL, away_4d_conv_pg REAL, away_4d_att_pg REAL, away_top REAL, 

        away_opp_ppg REAL, away_opp_pass_comp_pg REAL, away_opp_pass_yd_pg REAL, away_opp_pass_td_pg REAL, away_opp_int_thrown_pg REAL, away_opp_sacks_taken_pg REAL, away_opp_rush_att_pg REAL, away_opp_rush_yds_pg REAL, away_opp_rush_td_pg REAL, away_opp_fgm_pg REAL, away_opp_fga_pg REAL, away_opp_pnt_pg REAL, away_opp_3d_conv_pg REAL, away_opp_3d_att_pg REAL, away_opp_4d_conv_pg REAL, away_opp_4d_att_pg REAL, away_opp_top REAL,

        home_home_game_count INTEGER, home_away_game_count INTEGER, 

        home_ppg REAL, home_pass_comp_pg REAL, home_pass_yd_pg REAL, home_pass_td_pg REAL, home_int_thrown_pg REAL, home_sacks_taken_pg REAL, home_rush_att_pg REAL, home_rush_yds_pg REAL, home_rush_td_pg REAL, home_fgm_pg REAL, home_fga_pg REAL, home_pnt_pg REAL, home_3d_conv_pg REAL, home_3d_att_pg REAL, home_4d_conv_pg REAL, home_4d_att_pg REAL, home_top REAL, 

        home_opp_ppg REAL, home_opp_pass_comp_pg REAL, home_opp_pass_yd_pg REAL, home_opp_pass_td_pg REAL, home_opp_int_thrown_pg REAL, home_opp_sacks_taken_pg REAL, home_opp_rush_att_pg REAL, home_opp_rush_yds_pg REAL, home_opp_rush_td_pg REAL, home_opp_fgm_pg REAL, home_opp_fga_pg REAL, home_opp_pnt_pg REAL, home_opp_3d_conv_pg REAL, home_opp_3d_att_pg REAL, home_opp_4d_conv_pg REAL, home_opp_4d_att_pg REAL, home_opp_top REAL,
        
        UNIQUE(year, week, away, home) ON CONFLICT IGNORE)''')

    def insert_line_data(self, year, week, line_data_list):
        for line_data in line_data_list:
            self._insert_new_record(year, week, line_data['away'], line_data['home'])
            self._update_line_data(line_data['away_spread'], line_data['home_spread'], line_data['total_line'], year, week, line_data['away'], line_data['home'])

    def _update_line_data(self, away_spread, home_spread, total_line, year, week, away, home):
        cursor = self.conn.cursor()
        sql = f'UPDATE nfl_game_data SET away_spread={away_spread}, home_spread={home_spread}, total_line={total_line} WHERE year={year} AND week={week} AND away="{away}" AND home="{home}"'
        cursor.execute(sql)
        self.conn.commit()

    def _insert_new_record(self, year, week, away, home):
        cursor = self.conn.cursor()
        sql = f'INSERT INTO nfl_game_data(year, week, away, home) VALUES({year}, {week}, "{away}", "{home}")'
        cursor.execute(sql)
        self.conn.commit()

    def select_stats_needed(self):
        cursor = self.conn.cursor()
        sql = 'SELECT year, week, away, home FROM nfl_game_data WHERE away_pass_td_pg is NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        rows = result.fetchall()
        stats_needed_list = []
        for row in rows:
            row_as_dict = {
                'year': row[0],
                'week': row[1],
                'away': row[2],
                'home': row[3]}                
            stats_needed_list.append(row_as_dict)
        return stats_needed_list

    def insert_stats(self, stats_needed_list, stats):
        for game_data in stats_needed_list:
            year = game_data['year']
            week = game_data['week']
            away = game_data['away']
            home = game_data['home']
            awayStats = stats[away]
            homeStats = stats[home]
            cursor = self.conn.cursor()
            stat_values = (
                awayStats['home_game_count'], awayStats['away_game_count'], 
                awayStats['ppg'], awayStats['pass_comp_pg'], awayStats['pass_yd_pg'], awayStats['pass_td_pg'], awayStats['int_thrown_pg'], awayStats['sacks_taken_pg'], awayStats['rush_att_pg'], awayStats['rush_yds_pg'], awayStats['rush_td_pg'], awayStats['fgm_pg'], awayStats['fga_pg'], awayStats['pnt_pg'], awayStats['3d_conv_pg'], awayStats['3d_att_pg'], awayStats['4d_conv_pg'], awayStats['4d_att_pg'], awayStats['top'],
                awayStats['opp_ppg'], awayStats['opp_pass_comp_pg'], awayStats['opp_pass_yd_pg'], awayStats['opp_pass_td_pg'], awayStats['opp_int_thrown_pg'], awayStats['opp_sacks_taken_pg'], awayStats['opp_rush_att_pg'], awayStats['opp_rush_yds_pg'], awayStats['opp_rush_td_pg'], awayStats['opp_fgm_pg'], awayStats['opp_fga_pg'], awayStats['opp_pnt_pg'], awayStats['opp_3d_conv_pg'], awayStats['opp_3d_att_pg'], awayStats['opp_4d_conv_pg'], awayStats['opp_4d_att_pg'], awayStats['opp_top'],       
                homeStats['home_game_count'], homeStats['away_game_count'], 
                homeStats['ppg'], homeStats['pass_comp_pg'], homeStats['pass_yd_pg'], homeStats['pass_td_pg'], homeStats['int_thrown_pg'], homeStats['sacks_taken_pg'], homeStats['rush_att_pg'], homeStats['rush_yds_pg'], homeStats['rush_td_pg'], homeStats['fgm_pg'], homeStats['fga_pg'], homeStats['pnt_pg'], homeStats['3d_conv_pg'], homeStats['3d_att_pg'], homeStats['4d_conv_pg'], homeStats['4d_att_pg'], homeStats['top'],
                homeStats['opp_ppg'], homeStats['opp_pass_comp_pg'], homeStats['opp_pass_yd_pg'], homeStats['opp_pass_td_pg'], homeStats['opp_int_thrown_pg'], homeStats['opp_sacks_taken_pg'], homeStats['opp_rush_att_pg'], homeStats['opp_rush_yds_pg'], homeStats['opp_rush_td_pg'], homeStats['opp_fgm_pg'], homeStats['opp_fga_pg'], homeStats['opp_pnt_pg'], homeStats['opp_3d_conv_pg'], homeStats['opp_3d_att_pg'], homeStats['opp_4d_conv_pg'], homeStats['opp_4d_att_pg'], homeStats['opp_top'])
            sql = f'''
                UPDATE nfl_game_data SET away_home_game_count=?, away_away_game_count=?, 
        
                away_ppg=?, away_pass_comp_pg=?, away_pass_yd_pg=?, away_pass_td_pg=?, away_int_thrown_pg=?, away_sacks_taken_pg=?, away_rush_att_pg=?, away_rush_yds_pg=?, away_rush_td_pg=?, away_fgm_pg=?, away_fga_pg=?, away_pnt_pg=?, away_3d_conv_pg=?, away_3d_att_pg=?, away_4d_conv_pg=?, away_4d_att_pg=?, away_top=?, 

                away_opp_ppg=?, away_opp_pass_comp_pg=?, away_opp_pass_yd_pg=?, away_opp_pass_td_pg=?, away_opp_int_thrown_pg=?, away_opp_sacks_taken_pg=?, away_opp_rush_att_pg=?, away_opp_rush_yds_pg=?, away_opp_rush_td_pg=?, away_opp_fgm_pg=?, away_opp_fga_pg=?, away_opp_pnt_pg=?, away_opp_3d_conv_pg=?, away_opp_3d_att_pg=?, away_opp_4d_conv_pg=?, away_opp_4d_att_pg=?, away_opp_top=?,

                home_home_game_count=?, home_away_game_count=?, 

                home_ppg=?, home_pass_comp_pg=?, home_pass_yd_pg=?, home_pass_td_pg=?, home_int_thrown_pg=?, home_sacks_taken_pg=?, home_rush_att_pg=?, home_rush_yds_pg=?, home_rush_td_pg=?, home_fgm_pg=?, home_fga_pg=?, home_pnt_pg=?, home_3d_conv_pg=?, home_3d_att_pg=?, home_4d_conv_pg=?, home_4d_att_pg=?, home_top=?, 

                home_opp_ppg=?, home_opp_pass_comp_pg=?, home_opp_pass_yd_pg=?, home_opp_pass_td_pg=?, home_opp_int_thrown_pg=?, home_opp_sacks_taken_pg=?, home_opp_rush_att_pg=?, home_opp_rush_yds_pg=?, home_opp_rush_td_pg=?, home_opp_fgm_pg=?, home_opp_fga_pg=?, home_opp_pnt_pg=?, home_opp_3d_conv_pg=?, home_opp_3d_att_pg=?, home_opp_4d_conv_pg=?, home_opp_4d_att_pg=?, home_opp_top=? WHERE year={year} AND week={week} AND away="{away}" AND home="{home}"'''
            cursor.execute(sql, stat_values)
            self.conn.commit()

    def findYearWeekForUpdate(self):
        cursor = self.conn.cursor()
        sql = 'SELECT DISTINCT year, week FROM nfl_game_data WHERE away_score is NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        
        yearsAndWeeksList = []
        for row in result.fetchall():
            yearWeekDict = {}
            yearWeekDict['year'] = str(row[0])
            yearWeekDict['week'] = str(row[1])
            yearsAndWeeksList.append(yearWeekDict)

        return yearsAndWeeksList

    def updateScores(self, year, week, gameScoresList):
        cursor = self.conn.cursor()

        for gameScoreDict in gameScoresList:
            sqlAway = 'UPDATE nfl_game_data SET away_score=? WHERE away=? AND year=? AND week=?'
            valAway = (gameScoreDict['away_score'], gameScoreDict['away'], year, week)
            cursor.execute(sqlAway, valAway)

            sqlHome = 'UPDATE nfl_game_data SET home_score=? WHERE home=? AND year=? AND week=?'
            valHome = (gameScoreDict['home_score'], gameScoreDict['home'], year, week)
            cursor.execute(sqlHome, valHome)

        self.conn.commit()

    def selectAllData(self):
        cursor = self.conn.cursor()
        # sql = 'SELECT * FROM nfl_game_data WHERE away_score IS NOT NULL'
        sql = 'SELECT * FROM nfl_game_data'
        result = cursor.execute(sql)
        self.conn.commit()

        return result.fetchall()

    def selectHeaders(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nfl_game_data LIMIT 0'
        cursor.execute(sql)
        self.conn.commit()

        return [colTup[0] for colTup in cursor.description]

    # def selectCount(self, week, year):
    #     cursor = self.conn.cursor()
    #     sql = f'SELECT COUNT(*) FROM nfl_game_data WHERE week={week} and year={year}'
    #     cursor.execute(sql)
    #     result = cursor.fetchall()
    #     self.conn.commit()

    #     return result[0][0]





            
