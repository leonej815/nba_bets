import sqlite3

class Data_Storage:
    # connects to sqlite and creates table to store data if it doesn't exist
    def __init__(self):
        self.conn = sqlite3.connect('./sqlite/nba_bets.sqlite')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nba_game_data(
                date INTEGER, 
                away TEXT, 
                home TEXT, 
                away_spread REAL, 
                home_spread REAL, 
                total_line REAL, 
                away_score INTEGER, 
                home_score INTEGER, 
                away_offrtg REAL, 
                away_defrtg REAL, 
                away_reb_percent REAL, 
                away_tov_percent REAL, 
                away_ts_percent REAL, 
                away_pace REAL, 
                away_pie REAL, 
                home_offrtg REAL, 
                home_defrtg REAL, 
                home_reb_percent REAL, 
                home_tov_percent REAL, 
                home_ts_percent REAL, 
                home_pace REAL, 
                home_pie REAL, 
                UNIQUE(date, away, home) ON CONFLICT IGNORE
            )
        ''')
        self.conn.commit()

    # used create a game record and insert the spread lines, and total line into the database for that game
    def insert_line_data(self, date, line_data_list):
        for line_data in line_data_list:
            self._insert_new_record(date, line_data['away'], line_data['home'])
            self._update_line_data(
                line_data['away_spread'], 
                line_data['home_spread'], 
                line_data['total_line'], 
                date, 
                line_data['away'], 
                line_data['home']
            )

    # used to update the spread lines, and total line for a given game
    def _update_line_data(self, away_spread, home_spread, total_line, date, away, home):
        cursor = self.conn.cursor()
        sql = '''
            UPDATE nba_game_data 
            SET away_spread=?, home_spread=?, total_line=? 
            WHERE date=? AND away=? AND home=?
        '''
        cursor.execute(sql, (away_spread, home_spread, total_line, date, away, home))
        self.conn.commit()

    # inserts a new game record into the database
    def _insert_new_record(self, date, away, home):
        cursor = self.conn.cursor()
        sql = 'INSERT INTO nba_game_data(date, away, home) VALUES(?, ?, ?)'
        cursor.execute(sql, (date, away, home))
        self.conn.commit()

    # selects records where there is a game entry but the stats are NULL and need to be added
    # returns a list of dictionaries with the information about the games: date, away team, home team
    def select_stats_needed(self):
        cursor = self.conn.cursor()
        sql = 'SELECT date, away, home FROM nba_game_data WHERE away_offrtg IS NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        rows = result.fetchall()
        stats_needed_list = [
            {'date': row[0], 'away': row[1], 'home': row[2]} 
            for row in rows
        ]
        return stats_needed_list

    # takes a list of dictionaries with the information about games: date, away team, home team
    # also takes 2 level dictionary that contains the stats needed for all the teams in stats_needed_list
    # the function updates the records that correspond to the games in stats_needed_list with all the stats
    def insert_stats(self, stats_needed_list, stats):
        for game_data in stats_needed_list:
            date = game_data['date']
            away = game_data['away']
            home = game_data['home']
            cursor = self.conn.cursor()

            stat_values = (
                stats[away]['offrtg'], stats[away]['defrtg'], stats[away]['reb%'], stats[away]['tov%'], 
                stats[away]['ts%'], stats[away]['pace'], stats[away]['pie'], 
                stats[home]['offrtg'], stats[home]['defrtg'], stats[home]['reb%'], stats[home]['tov%'], 
                stats[home]['ts%'], stats[home]['pace'], stats[home]['pie']
            )

            sql = '''
                UPDATE nba_game_data 
                SET away_offrtg=?, away_defrtg=?, away_reb_percent=?, away_tov_percent=?, 
                    away_ts_percent=?, away_pace=?, away_pie=?, 
                    home_offrtg=?, home_defrtg=?, home_reb_percent=?, home_tov_percent=?, 
                    home_ts_percent=?, home_pace=?, home_pie=? 
                WHERE date=? AND away=? AND home=?
            '''
            cursor.execute(sql, stat_values + (date, away, home))
            self.conn.commit()

    # returns a list of dates where there are game records without the final score added
    def find_dates_for_scores(self):
        cursor = self.conn.cursor()
        sql = 'SELECT DISTINCT date FROM nba_game_data WHERE away_score IS NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        return [str(date[0]) for date in result.fetchall()]

    # game_scores_list is a list of dictionaries that have the away team, home team, away score, and home score
    # for a given date this function updates all the records for that date with final scores using game_scores_list
    def update_scores(self, date, game_scores_list):
        cursor = self.conn.cursor()
        for game_score_dict in game_scores_list:
            # Update away scores
            sql_away = 'UPDATE nba_game_data SET away_score=? WHERE away=? AND date=?'
            val_away = (game_score_dict['away_score'], game_score_dict['away'], date)
            cursor.execute(sql_away, val_away)

            # Update home scores
            sql_home = 'UPDATE nba_game_data SET home_score=? WHERE home=? AND date=?'
            val_home = (game_score_dict['home_score'], game_score_dict['home'], date)
            cursor.execute(sql_home, val_home)

        self.conn.commit()

    def select_all_data(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nba_game_data'
        result = cursor.execute(sql)
        self.conn.commit()
        return result.fetchall()

    def select_betting_data(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nba_game_data WHERE away_score IS NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        headers = self.selectHeaders()
        rows = result.fetchall()
        betting_data = [
            {headers[i]: row[i] for i in range(len(row))} 
            for row in rows
        ]
        return betting_data

    def select_headers(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nba_game_data LIMIT 0'
        cursor.execute(sql)
        self.conn.commit()
        return [col_tup[0] for col_tup in cursor.description]