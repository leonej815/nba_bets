import sqlite3

class Data_Storage:
    """
    A class for managing NBA game data storage using an SQLite database.
    """

    def __init__(self):
        """
        Initializes the SQLite connection and creates the `nba_game_data` table if it does not already exist.
        """
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

    def insert_line_data(self, date, line_data_list):
        """
        Inserts or updates NBA line data for a specific date.

        Args:
            date (int): The date of the game in 'yyyymmdd' format.
            line_data_list (list): A list of dictionaries containing game line data.
        """
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

    def _update_line_data(self, away_spread, home_spread, total_line, date, away, home):
        """
        Updates line data for a specific game.

        Args:
            away_spread (float): The spread for the away team.
            home_spread (float): The spread for the home team.
            total_line (float): The total line for the game.
            date (int): The date of the game in 'yyyymmdd' format.
            away (str): The name of the away team.
            home (str): The name of the home team.
        """
        cursor = self.conn.cursor()
        sql = '''
            UPDATE nba_game_data 
            SET away_spread=?, home_spread=?, total_line=? 
            WHERE date=? AND away=? AND home=?
        '''
        cursor.execute(sql, (away_spread, home_spread, total_line, date, away, home))
        self.conn.commit()

    def _insert_new_record(self, date, away, home):
        """
        Inserts a new record for a game into the database.

        Args:
            date (int): The date of the game in 'yyyymmdd' format.
            away (str): The name of the away team.
            home (str): The name of the home team.
        """
        cursor = self.conn.cursor()
        sql = 'INSERT INTO nba_game_data(date, away, home) VALUES(?, ?, ?)'
        cursor.execute(sql, (date, away, home))
        self.conn.commit()

    def select_stats_needed(self):
        """
        Selects games that are missing advanced stats.

        Returns:
            list: A list of dictionaries with the date, away team, and home team for games missing stats.
        """
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

    def insert_stats(self, stats_needed_list, stats):
        """
        Updates advanced stats for games in the database.

        Args:
            stats_needed_list (list): A list of games that require stats.
            stats (dict): A dictionary of stats keyed by team names.
        """
        for game_data in stats_needed_list:
            date = game_data['date']
            away = game_data['away']
            home = game_data['home']
            cursor = self.conn.cursor()

            # Extract stats for away and home teams
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

    def findDatesForScores(self):
        """
        Finds dates for games that are missing scores.

        Returns:
            list: A list of dates as strings where scores are missing.
        """
        cursor = self.conn.cursor()
        sql = 'SELECT DISTINCT date FROM nba_game_data WHERE away_score IS NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        return [str(date[0]) for date in result.fetchall()]

    def updateScores(self, date, gameScoresList):
        """
        Updates scores for games in the database.

        Args:
            date (int): The date of the games in 'yyyymmdd' format.
            gameScoresList (list): A list of dictionaries containing game scores.
        """
        cursor = self.conn.cursor()
        for gameScoreDict in gameScoresList:
            # Update away scores
            sqlAway = 'UPDATE nba_game_data SET away_score=? WHERE away=? AND date=?'
            valAway = (gameScoreDict['away_score'], gameScoreDict['away'], date)
            cursor.execute(sqlAway, valAway)

            # Update home scores
            sqlHome = 'UPDATE nba_game_data SET home_score=? WHERE home=? AND date=?'
            valHome = (gameScoreDict['home_score'], gameScoreDict['home'], date)
            cursor.execute(sqlHome, valHome)

        self.conn.commit()

    def selectAllData(self):
        """
        Selects all data from the `nba_game_data` table.

        Returns:
            list: A list of tuples containing all rows in the table.
        """
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nba_game_data'
        result = cursor.execute(sql)
        self.conn.commit()
        return result.fetchall()

    def select_betting_data(self):
        """
        Selects games missing scores, typically for betting purposes.

        Returns:
            list: A list of dictionaries containing games without scores.
        """
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

    def selectHeaders(self):
        """
        Retrieves the column headers of the `nba_game_data` table.

        Returns:
            list: A list of column names.
        """
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nba_game_data LIMIT 0'
        cursor.execute(sql)
        self.conn.commit()
        return [colTup[0] for colTup in cursor.description]