class Nba_Criteria:
    """
    A class for applying various criteria to NBA game data to make predictions
    about game outcomes, including over/under total line picks and spread picks.
    """

    def get_ppg_total_pick(self, game_data):
        """
        Predicts whether the total points scored in a game will go over or under the betting line.

        Args:
            game_data (dict): A dictionary containing game data, including offensive ratings,
                              pace, and total line.

        Returns:
            str: 'o' for over, 'u' for under, and 'na' for no action.
        """
        away_ppg = game_data['away_offrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['home_offrtg'] * game_data['home_pace'] / 100
        ppg_total = away_ppg + home_ppg
        total_line = game_data['total_line']
        if ppg_total - total_line > 4:
            return 'o'  # Over
        elif total_line - ppg_total > 4:
            return 'u'  # Under
        else:
            return 'na'  # No action

    def get_ts_reb_tov_spread_pick(self, game_data):
        """
        Predicts the spread pick based on true shooting percentage, rebound percentage,
        and turnover percentage.

        Args:
            game_data (dict): A dictionary containing game data, including TS%, REB%, and TOV%.

        Returns:
            str: 'a' for away team, 'h' for home team, and 'na' for no action.
        """
        away_stat = (game_data['away_ts_percent'] + game_data['away_reb_percent'] - game_data['away_tov_percent']) * 1.2
        home_stat = (game_data['home_ts_percent'] + game_data['home_reb_percent'] - game_data['home_tov_percent']) * 1.2
        away_spread_prediction = home_stat - away_stat + 3
        home_spread_prediction = away_stat - home_stat - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -6:
            return 'a'  # Away team
        elif home_spread_prediction - home_spread < -6:
            return 'h'  # Home team
        else:
            return 'na'  # No action       

    def get_ppg_spread_pick(self, game_data):
        """
        Predicts the spread pick based on points per game (PPG).

        Args:
            game_data (dict): A dictionary containing game data, including offensive ratings,
                              pace, and spreads.

        Returns:
            str: 'a' for away team, 'h' for home team, and 'na' for no action.
        """
        away_ppg = game_data['away_offrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['home_offrtg'] * game_data['home_pace'] / 100
        away_spread_prediction = home_ppg - away_ppg + 3
        home_spread_prediction = away_ppg - home_ppg - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -5:
            return 'a'  # Away team
        elif home_spread_prediction - home_spread < -5:
            return 'h'  # Home team
        else:
            return 'na'  # No action      

    def get_drtg_pace_spread_pick(self, game_data):
        """
        Predicts the spread pick based on defensive rating (DRtg) and pace.

        Args:
            game_data (dict): A dictionary containing game data, including defensive ratings,
                              pace, and spreads.

        Returns:
            str: 'a' for away team, 'h' for home team, and 'na' for no action.
        """
        away_ppg = game_data['home_defrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['away_defrtg'] * game_data['home_pace'] / 100
        away_spread_prediction = home_ppg - away_ppg + 3
        home_spread_prediction = away_ppg - home_ppg - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -3:
            return 'a'  # Away team
        elif home_spread_prediction - home_spread < -3:
            return 'h'  # Home team
        else:
            return 'na'  # No action      

    def get_avg_pace_ortg_drtg_spread_pick(self, game_data):
        """
        Predicts the spread pick based on average pace, offensive rating (ORtg), and defensive rating (DRtg).

        Args:
            game_data (dict): A dictionary containing game data, including ORtg, DRtg, pace, and spreads.

        Returns:
            str: 'a' for away team, 'h' for home team, and 'na' for no action.
        """
        avg_pace = (game_data['away_pace'] + game_data['home_pace']) / 2
        away_ortg_home_drtg = (game_data['away_offrtg'] + game_data['home_defrtg']) / 2
        home_ortg_away_drtg = (game_data['home_offrtg'] + game_data['away_defrtg']) / 2
        away_score_prediction = away_ortg_home_drtg * avg_pace / 100
        home_score_prediction = home_ortg_away_drtg * avg_pace / 100
        away_spread_prediction = home_score_prediction - away_score_prediction + 3
        home_spread_prediction = away_score_prediction - home_score_prediction - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -3:
            return 'a'  # Away team
        elif home_spread_prediction - home_spread < -3:
            return 'h'  # Home team
        else:
            return 'na'  # No action