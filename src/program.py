import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
from os import path
import pandas as pd
import requests
import scipy
import seaborn as sn
import streamlit as st

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


def load_pickle(file_name):
    pickle = pd.read_pickle(f'data/{file_name}')
    return pickle


def fetch_and_save_matches(tournaments_df, file_name):
    # Only take matches from tournaments that have passed.
    #results_df = tournaments_df.loc[tournaments_df['Type'] == 'results']
    results_df = tournaments_df
    tournament_ids = results_df['TournamentID'].values.tolist()
    tournament_start_dates = results_df['StartDate'].values.tolist()
    tournament_end_dates = results_df['EndDate'].values.tolist()
    dates_ids = list(zip(tournament_ids, tournament_start_dates, tournament_end_dates))
    matches_js = []
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
    matches_df = pd.DataFrame(matches_js, columns=matches_js[0].keys())
    matches_df.to_pickle(f'data/{file_name}')


def get_player_matches(matches_df, player_name):
    player_matches = matches_df.loc[(matches_df['hPlayerName'] == player_name) | (matches_df['vPlayerName'] == player_name)]
    return player_matches






st.set_page_config(
     page_title="Club Locker Analytics",
     page_icon="🎾",
     layout="centered",
     initial_sidebar_state="collapsed",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )





st.sidebar.write('Sidebar text')
st.sidebar.button("Click me!")


st.write("# Clublocker Exploratory Data Analysis")



current_date = datetime.datetime.now().date()

if not path.exists(f'data/tournaments_{str(current_date)}.pkl'):
    with st.spinner("Loading tournament data from Club Locker, please be patient..."):
        fetch_and_save_tournaments(file_name=f'tournaments_{str(current_date)}.pkl')
tournaments_df = load_pickle(file_name=f'tournaments_{str(current_date)}.pkl')
tournaments_df['StartDatePandas'] = pd.to_datetime(tournaments_df['StartDate'])
tournaments_filtered = tournaments_df[tournaments_df['NumMatches'] > 0]
st.success(f"Tournament data covers {len(tournaments_filtered)} tournaments starting from {str(tournaments_df['StartDatePandas'].min().date())} and ending in {str(tournaments_df['StartDatePandas'].max().date())}.")

if not path.exists(f'data/matches_{str(current_date)}.pkl'):
    with st.spinner("Loading match data from Club Locker. This can take a while, please be patient..."):
        fetch_and_save_matches(tournaments_filtered, file_name=f'matches_{str(current_date)}.pkl')
matches_df = load_pickle(file_name=f'matches_{str(current_date)}.pkl')

matches_df['MatchDatePandas'] = pd.to_datetime(matches_df['MatchDate'])
matches_df['Game1'] = (matches_df['wset1'] + matches_df['oset1']).fillna(0)
matches_df['Game2'] = (matches_df['wset2'] + matches_df['oset2']).fillna(0)
matches_df['Game3'] = (matches_df['wset3'] + matches_df['oset3']).fillna(0)
matches_df['Game4'] = (matches_df['wset4'] + matches_df['oset4']).fillna(0)
matches_df['Game5'] = (matches_df['wset5'] + matches_df['oset5']).fillna(0)
matches_df['NumberOfGames'] = (matches_df[['Game1', 'Game2', 'Game3', 'Game4', 'Game5']] != 0).astype(int).sum(axis=1)
matches_df['MatchDuration'] = pd.to_datetime(matches_df['matchEnd']) - pd.to_datetime(matches_df['matchStart'])
matches_df = matches_df.loc[matches_df['MatchDuration'] < pd.Timedelta(2, 'h')]
matches_df = matches_df.loc[matches_df['MatchDuration'] > pd.Timedelta(4, 'm')]
matches_df['MatchDuration'] = matches_df['MatchDuration'].astype('timedelta64[m]')
matches_df['Rallies'] = matches_df[['wset1', 'oset1', 'wset2', 'oset2', 'wset3', 'oset3', 'wset4', 'oset4', 'wset5', 'oset5']].dropna().sum(axis=1)
st.success(f"Match data covers {len(matches_df)} matches starting from {str(matches_df['MatchDatePandas'].min().date())} and ending in {str(matches_df['MatchDatePandas'].max().date())}.")





import datetime as dt

# Mark covid
start_dates = pd.to_datetime(tournaments_filtered['StartDate'].values.tolist())
covid = []
for start_date in start_dates:
    if start_date < pd.to_datetime('2020-03-01'):
        covid.append(0)
    else:
        covid.append(1)
tournaments_filtered['covid'] = covid



tournaments_filtered['StartDateTimeStamp'] = pd.to_datetime(tournaments_filtered['StartDate'])
tournaments_filtered['StartDateTimeStamp'] = tournaments_filtered['StartDateTimeStamp'].map(dt.datetime.toordinal)



plt.style.use('ggplot')
fig, ax = plt.subplots()
ax.set_xlabel('Ordinal timestamp')
ax.set_ylabel('Number of matches in tournament')
tournaments_filtered_nocovid = tournaments_filtered.loc[tournaments_filtered['covid'] == 0]
tournaments_filtered_yescovid = tournaments_filtered.loc[tournaments_filtered['covid'] == 1]
ax.plot(tournaments_filtered_nocovid['StartDateTimeStamp'], tournaments_filtered_nocovid['NumMatches'], 'g.', label='Pre-covid')
ax.plot(tournaments_filtered_yescovid['StartDateTimeStamp'], tournaments_filtered_yescovid['NumMatches'], 'r.', label='Post-covid')
window = 10
rolling_average = tournaments_filtered['NumMatches'].rolling(window, center=True).mean()
ax.plot(tournaments_filtered['StartDateTimeStamp'], rolling_average, 'y', label=f'Rolling avg over {window} tournaments')
m, b = np.polyfit(tournaments_filtered['StartDateTimeStamp'], tournaments_filtered['NumMatches'], 1)
ax.plot(tournaments_filtered['StartDateTimeStamp'], m * tournaments_filtered['StartDateTimeStamp'] + b, linewidth=2, label='Linear trend')
ax.legend()



st.write('### Tournaments')
st.caption('Number of matches in each of the tournaments. All canceled tournaments are excluded from the data.')
st.pyplot(fig)




st.write('### Match analytics')
# Filter out some early weird data, not valid matches, etc.
matches_subset = matches_df.loc[(matches_df['matchid'] > 1000000) & (matches_df['Rallies'] > 20)]
fig2, ax2 = plt.subplots(1, 2)
ax2[0].set_xlabel('Number of Rallies')
ax2[0].set_ylabel('Match count')
sn.scatterplot(ax=ax2[0], x=matches_subset.groupby(by='Rallies').count()['matchid'].index, y=matches_subset.groupby(by='Rallies').count()['matchid'].values.tolist(), palette='flare')
ax2[1].set_xlabel('Number of Rallies')
ax2[1].set_ylabel('Density')
sn.kdeplot(ax=ax2[1], data=matches_df, x='Rallies', palette='flare', bw_adjust=.5)
st.pyplot(fig2)



selected_tournament = st.selectbox('Select the tournament name', tournaments_filtered['TournamentName'].loc[tournaments_filtered['Type'] == 'results'])
selected_tournament_id = tournaments_filtered.loc[tournaments_filtered['TournamentName'] == selected_tournament]['TournamentID'].values[0]
selected_matches = matches_df.loc[matches_df['TournamentID'] == selected_tournament_id]
st.success(f'Selected {len(selected_matches)} matches from {selected_tournament}')
fig3, ax3 = plt.subplots()
ax3.set_xlabel('Time')
ax3.set_ylabel('Number of Rallies')
matches_subset = matches_df.loc[matches_df['TournamentID'] == selected_tournament_id][['matchStart', 'Rallies']].dropna()
matches_subset = matches_subset.loc[pd.to_datetime(matches_subset['matchStart']) > pd.to_datetime('01-01-2018T00:00:00.000Z')]
ax3.plot(pd.to_datetime(matches_subset['matchStart']), matches_subset['Rallies'], 'g.')
st.pyplot(fig3)



### Multiselect
selected_tournaments = st.multiselect('Select tournaments', tournaments_filtered['TournamentName'].loc[tournaments_filtered['Type'] == 'results'])
selected_tournament_ids = tournaments_filtered.loc[tournaments_filtered['TournamentName'].isin(selected_tournaments)]['TournamentID'].values.tolist()
###



fig4, ax4 = plt.subplots()
ax4.set_xlabel('Match duration (minutes)')
ax4.set_ylabel('Number of Rallies')
g = sn.scatterplot(data=matches_df.loc[matches_df['NumberOfGames'] >= 3], x='MatchDuration', y='Rallies', hue='NumberOfGames', size='NumberOfGames', palette='flare', alpha=0.8)
g.set(xlim=(0,90))
#sn.scatterplot(data=matches_df.loc[(matches_df['NumberOfGames'] >= 3) & (matches_df['TournamentID'].isin(selected_tournament_ids))], x='MatchDuration', y='Rallies', hue='NumberOfGames', size='NumberOfGames', palette='flare', alpha=0.8)
st.pyplot(fig4)



fig5, ax5 = plt.subplots()
g = sn.kdeplot(data=matches_df.loc[matches_df['NumberOfGames'] >= 3], x='MatchDuration', hue='NumberOfGames', palette='flare', fill=True, alpha=0.5)
g.set(xlim=(0,90))
ax5.set_xlabel('Match duration (minutes)')
st.pyplot(fig5)



# TODO: Figure out why sort_values does not work with ns.PairGrid
# sample = matches_df.loc[matches_df['NumberOfGames'] >= 3].sample(50).sort_values('Rallies', ascending=False).reset_index(drop=True)
# x_cols = ['Rallies', 'MatchDuration', 'NumberOfGames']
# g = sn.PairGrid(sample, x_vars=x_cols, y_vars=['matchid'], height=10, aspect=0.25)
# g.map(sn.stripplot, size=10, orient='h', jitter=False, palette='flare', linewidth=1, edgecolor='w')
# g.set(ylabel='Match ID')
# for ax, title in zip(g.axes.flat, x_cols):
#     ax.set(title=title)
#     ax.xaxis.grid(False)
#     ax.yaxis.grid(True)
# sn.despine(left=True, bottom=True)
# st.pyplot(g)




name = st.text_input('Player name', 'Search here!')
matches_df_dropna = matches_df.dropna(subset=['vPlayerName', 'hPlayerName'])
search_results = matches_df_dropna.loc[matches_df_dropna['vPlayerName'].str.contains(name, case=False) | matches_df_dropna['hPlayerName'].str.contains(name, case=False)]
st.dataframe(search_results[['matchid', 'hPlayerName', 'vPlayerName', 'Score_Short', 'Winner', 'Rallies']])
st.caption(f'Found {len(search_results)} matches')





# with st.form("my_form"):
#     st.write("Inside the form")
#     slider_val = st.slider("Form slider")
#     checkbox_val = st.checkbox("Form checkbox")
#     # Every form must have a submit button.
#     submitted = st.form_submit_button("Submit")
#     if submitted:
#         st.write("slider", slider_val, "checkbox", checkbox_val)
# st.write("Outside the form")



# Instead of corr() maybe find
# fig3, ax3 = plt.subplots()
# normal_columns = ['TournamentID', 'PlayersOnDraw', 'NumMatches']
# cat_columns = ['TournamentContact', 'TournamentName', 'StartDate', 'EndDate', 'SiteCity', 'Entry_Open', 'Entry_Close', 'Entry_Close_Time', 'EarlyBirdRegistrationDeadline', 'Registration_Deadline', 'VenueId', 'EventType', 'EventTypeCode', 'EntryForm', 'CreateDate', 'UpdateDate', 'VenueName', 'Type']
# for cat_column in cat_columns:
#     tournaments_df[cat_column] = tournaments_df[cat_column].astype('category').cat.codes
# sn.heatmap(tournaments_df[normal_columns+cat_columns].corr(), annot=False, cmap='coolwarm')
# st.pyplot(fig3)