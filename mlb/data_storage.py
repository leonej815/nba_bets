import sqlite3

class Data_Storage:
    def __init__(self):
        self.conn = sqlite3.connect('./sqlite/sports_bets.sqlite')
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS mlb_game_data(date INTEGER, away TEXT, home TEXT, away_spread REAL, home_spread REAL, total_line REAL, away_score INTEGER, home_score INTEGER, away_runs_per_inning REAL, away_runs_allowed_per_inning REAL, home_runs_per_inning REAL, home_runs_allowed_per_inning REAL, UNIQUE(date, away, home) ON CONFLICT IGNORE)')
        self.conn.commit()

    def insert_line_data(self, date, line_data_list):
        for line_data in line_data_list:
            self._insert_new_record(date, line_data['away'], line_data['home'])
            self._update_line_data(line_data['away_spread'], line_data['home_spread'], line_data['total_line'], date, line_data['away'], line_data['home'])

    def _update_line_data(self, away_spread, home_spread, total_line, date, away, home):
        cursor = self.conn.cursor()
        sql = f'UPDATE mlb_game_data SET away_spread={away_spread}, home_spread={home_spread}, total_line={total_line} WHERE date={date} AND away="{away}" AND home="{home}"'
        cursor.execute(sql)
        self.conn.commit()

    def _insert_new_record(self, date, away, home):
        cursor = self.conn.cursor()
        sql = f'INSERT INTO mlb_game_data(date, away, home) VALUES({date}, "{away}", "{home}")'
        cursor.execute(sql)
        self.conn.commit()

    def select_stats_needed(self):
        cursor = self.conn.cursor()
        sql = 'SELECT date, away, home FROM mlb_game_data WHERE away_offrtg is NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        rows = result.fetchall()
        stats_needed_list = []
        for row in rows:
            row_as_dict = {
                'date': row[0],
                'away': row[1],
                'home': row[2]}                
            stats_needed_list.append(row_as_dict)
        return stats_needed_list

    def insert_stats(self, stats_needed_list, stats):
        for game_data in stats_needed_list:
            date = game_data['date']
            away = game_data['away']
            home = game_data['home']
            cursor = self.conn.cursor()
            stat_values = (stats[away]['runs_per_inning'], stats[away]['runs_allowed_per_inning'], stats[home]['runs_per_inning'], stats[home]['runs_allowed_per_inning'])
            sql = f'UPDATE mlb_game_data SET away_runs_per_inning=?, away_runs_allowed_per_inning=?, home_runs_per_inning=?, home_runs_allowed_per_inning=? WHERE date={date} AND away="{away}" AND home="{home}"'
            cursor.execute(sql, stat_values)
            self.conn.commit()

    def findDatesForScores(self):
        cursor = self.conn.cursor()
        sql = 'SELECT DISTINCT date FROM mlb_game_data WHERE away_score is NULL'
        result = cursor.execute(sql)
        self.conn.commit()

        return [str(date) for tup in result.fetchall() for date in tup] # removes singleton tuples


    def updateScores(self, date, gameScoresList):
        cursor = self.conn.cursor()

        for gameScoreDict in gameScoresList:
            sqlAway = 'UPDATE mlb_game_data SET away_score=? WHERE away=? AND date=?'
            valAway = (gameScoreDict['away_score'], gameScoreDict['away'], date)
            cursor.execute(sqlAway, valAway)

            sqlHome = 'UPDATE mlb_game_data SET home_score=? WHERE home=? AND date=?'
            valHome = (gameScoreDict['home_score'], gameScoreDict['home'], date)
            cursor.execute(sqlHome, valHome)

        self.conn.commit()


    def selectAllData(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM mlb_game_data'
        # sql = 'SELECT * FROM game_data WHERE away_score IS NOT NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        return result.fetchall()

    def select_betting_data(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM mlb_game_data WHERE away_score IS NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        headers = self.selectHeaders()
        rows = result.fetchall()
        betting_data = []
        for row in rows:
            row_as_dict = {headers[i]:row[i] for i in range(len(row))}
            betting_data.append(row_as_dict)
        return betting_data


    def selectHeaders(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM mlb_game_data LIMIT 0'
        cursor.execute(sql)
        self.conn.commit()
        return [colTup[0] for colTup in cursor.description]




            
