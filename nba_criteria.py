class Nba_Criteria:
    def get_ppg_total_pick(self, game_data):
        away_ppg = game_data['away_offrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['home_offrtg'] * game_data['home_pace'] / 100
        ppg_total = away_ppg + home_ppg
        total_line = game_data['total_line']
        if ppg_total - total_line > 4:
            return 'o'
        elif total_line - ppg_total > 4:
            return 'u'
        else:
            return 'na'

    def get_ts_reb_tov_spread_pick(self, game_data):
        away_stat = (game_data['away_ts_percent'] + game_data['away_reb_percent'] - game_data['away_tov_percent']) * 1.2
        home_stat = (game_data['home_ts_percent'] + game_data['home_reb_percent'] - game_data['home_tov_percent']) * 1.2
        away_spread_prediction = home_stat - away_stat + 3
        home_spread_prediction = away_stat - home_stat - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -6:
            return 'a'
        elif home_spread_prediction - home_spread < -6:
            return 'h'
        else:
            return 'na'       

    def get_ppg_spread_pick(self, game_data):
        away_ppg = game_data['away_offrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['home_offrtg'] * game_data['home_pace'] / 100
        away_spread_prediction = home_ppg - away_ppg + 3
        home_spread_prediction = away_ppg - home_ppg - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -5:
            return 'a'
        elif home_spread_prediction - home_spread < -5:
            return 'h'
        else:
            return 'na'      

    def get_drtg_pace_spread_pick(self, game_data):
        away_ppg = game_data['home_defrtg'] * game_data['away_pace'] / 100
        home_ppg = game_data['away_defrtg'] * game_data['home_pace'] / 100
        away_spread_prediction = home_ppg - away_ppg + 3
        home_spread_prediction = away_ppg - home_ppg - 3
        away_spread = game_data['away_spread']
        home_spread = game_data['home_spread']
        if away_spread_prediction - away_spread < -3:
            return 'a'
        elif home_spread_prediction - home_spread < -3:
            return 'h'
        else:
            return 'na'      

    def get_avg_pace_ortg_drtg_spread_pick(self, game_data):
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
            return 'a'
        elif home_spread_prediction - home_spread < -3:
            return 'h'
        else:
            return 'na'    
        


        