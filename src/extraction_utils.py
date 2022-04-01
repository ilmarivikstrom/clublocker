import json
import pandas as pd
import requests


def fetch_and_save_tournaments(file_name):
    tournament_types = {'scheduled': 1, 'results': 3}
    tournaments = []
    for tournament_type in tournament_types:
        response = requests.get(url=f'https://api.ussquash.com/resources/tournaments?TopRecords=500&ngbId=10142&OrganizerType=1&Sanctioned=1&Status={tournament_types[tournament_type]}')
        js = json.loads(response.content)
        for tournament in js:
            tournament['Type'] = tournament_type
            tournaments.append(tournament)
            print(f'Tournament type: {tournament_type}')
            print(f"Name: {tournament['TournamentName']}, {tournament['StartDate']} - {tournament['EndDate']}")
        print('\n')
    tournaments_df = pd.DataFrame(tournaments, columns=tournaments[0].keys())
    tournaments_df.to_pickle(f'data/{file_name}')


def fetch_and_save_tournament_matches(tournaments_df, file_name):
    # Only take matches from tournaments that have passed.
    #results_df = tournaments_df.loc[tournaments_df['Type'] == 'results']
    results_df = tournaments_df
    tournament_ids = results_df['TournamentID'].values.tolist()
    tournament_start_dates = results_df['StartDate'].values.tolist()
    tournament_end_dates = results_df['EndDate'].values.tolist()
    dates_ids = list(zip(tournament_ids, tournament_start_dates, tournament_end_dates))
    matches_js = []
    index = 0
    my_bar = st.progress(0)
    for tournament in dates_ids:
        if (tournament[0] == 13512):
            print('Dunlop Cup')
        date_range_list = [str(x.date()) for x in pd.date_range(tournament[1], tournament[2])]
        for date in date_range_list:
            response = requests.get(url = f'https://api.ussquash.com/resources/res/trn/live_matrix?date={date}&tournamentId={tournament[0]}')
            js = json.loads(response.content)
            for entry in js:
                if len(entry) > 1:
                    entry['TournamentID'] = tournament[0]
                    matches_js.append(entry)
        print(f'Fetched matches from tournament {tournament[0]}. Total matches loaded: {len(matches_js)}')
        index += 1
        my_bar.progress(index/len(dates_ids))
    matches_df = pd.DataFrame(matches_js, columns=matches_js[0].keys())
    matches_df.to_pickle(f'data/{file_name}')


def fetch_rankings(file_name):
    ranking_urls = ['https://api.ussquash.com/resources/rankings?RowsPerPage=1000&PageNumber=1&Rating_GroupID=9&Season=2021-2022&main=10142&DivisionId=2', 'https://api.ussquash.com/resources/rankings?RowsPerPage=1000&PageNumber=1&Rating_GroupID=9&Season=2021-2022&main=10142&DivisionId=1']
    rankings = []
    for ranking_url in ranking_urls:
        response = requests.get(ranking_url)
        js = json.loads(response.content)
        for entry in js:
            entry['LastName'] = entry['PlayerName'].replace(' ', '').split(',')[0]
            entry['FirstName'] = entry['PlayerName'].replace(' ', '').split(',')[1]
            rankings.append(entry)
    rankings_df = pd.DataFrame(rankings, columns=rankings[0].keys())
    rankings_df.to_pickle(f'data/{file_name}')
    

def load_pickle(file_name):
    pickle = pd.read_pickle(f'data/{file_name}')
    return pickle