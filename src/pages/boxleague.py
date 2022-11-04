# TODO: Liigat: https://api.ussquash.com/resources/leagues?TopRecords=50&OrganizationId=10142&Admin=false&Status=0 --> & status 1 --> leagueid
# TODO: Liiga: https://api.ussquash.com/resources/leagues/results/606 --> scorecardid
# TODO: Scorecard: https://api.ussquash.com/resources/leagues/scorecards/live?id=133473
import streamlit as st


def app():
    import numpy as np
    import pandas as pd
    import requests

    #year = st.radio('Select the year:', [2022, 2021, 2020])
    year = 2022
    st.title('Box League results')

    def fetch_data():
        headers = {"Authorization": "Bearer MdjxJVbgPBaorOcKtYFPIitv33Dk33G81YpdWYSAAl7748wY62KBwcxAzbJ7HgcNswxeKfi3jPsKktbhQzwMtvitiiP1tRiprXgqjosQh13cC5UtENkYE4fJdeGDYzK2ba4Ca63kANnXj09ZEkOLYf0MwQgVhp5N1TZIi9B264tCfVYiBak3D1nIvAs212dBTWtte320ht1RkwUVLEC6TPmeB5YvIB9ZoWV31Y8iyflBc2lWgCIZNmVBkNIWCADJ"}
        # Requires auth.
        boxes_response = requests.get(url='https://api.ussquash.com/resources/res/box_leagues/list?TopRecords=50&clubId=10209', headers=headers)
        boxes_df = pd.read_json(boxes_response.text)
        box_ids = boxes_df['eventId'].loc[(pd.to_datetime(boxes_df['startDate']) > pd.to_datetime(f"{year}-01-01T00:00:00")) & (pd.to_datetime(boxes_df['endDate']) < pd.to_datetime(f"{year+1}-01-01T00:00:00"))].unique().tolist()

        boxes = []

        for box_id in box_ids:
            players_response = requests.get(url=f'https://api.ussquash.com/resources/res/box_leagues/{box_id}/players', headers=headers)
            players_df = pd.read_json(players_response.text)
            standings_response = requests.get(url=f'https://api.ussquash.com/resources/res/box_leagues/{box_id}/standings', headers=headers)
            standings_df = pd.read_json(standings_response.text)
            results_response = requests.get(url=f'https://api.ussquash.com/resources/res/box_leagues/{box_id}/results')
            results_df = pd.read_json(results_response.text)
            one_box_contents = {"box": boxes_df.loc[boxes_df["eventId"] == box_id], "players": players_df, "standings": standings_df, "results": results_df}
            boxes.append(one_box_contents)
        return boxes

    boxes = fetch_data()

    standings_df = pd.DataFrame()
    results_df = pd.DataFrame()

    for history in range(len(boxes)):
        standings_df = pd.concat([standings_df, boxes[history]['standings']], ignore_index=True)
        results_df = pd.concat([results_df, boxes[history]['results']], ignore_index=True)

    standings_df = standings_df.groupby(by=["PlayerName"]).sum()
    standings_df["Name"] = standings_df.index

    standings_df["Win_Percentage"] = round(standings_df["Wins_Season"] / (standings_df["Wins_Season"] + standings_df["Loses_Season"]) * 100, 1).astype(str).astype(str) + ' %'
    
    standings_table = standings_df.sort_values(by=['Points_Season'], ascending=False)[['Name', 'Wins_Season', 'Loses_Season', 'Points_Season', 'Win_Percentage']]
    standings_table['Rank'] = np.arange(len(standings_table)) + 1
    standings_table = standings_table.rename(columns = {'Rank':'Rank', 'Wins_Season':'Wins', 'Loses_Season':'Losses', 'Points_Season': 'Points', 'Win_Percentage': 'Win Percentage'}, inplace = False)
    standings_table['Name'] = standings_table.index

    standings_table = standings_table.reset_index().set_index(np.arange(len(standings_table))+1)

    standings_table = standings_table[['Rank', 'Name', 'Wins', 'Losses', 'Points', 'Win Percentage']]

    def custom_style(row):
        if row.values[0] == 1:
            return ['background-color: #e6c200']*len(row.values)
        if row.values[0] == 2:
            return ['background-color: #818181']*len(row.values)
        if row.values[0] == 3:
            return ['background-color: #905923']*len(row.values)

    standings_table_colored = standings_table.style.apply(custom_style, axis=1)

    number_of_players = len(standings_table)
    st.text('Season standings:')
    st.dataframe(standings_table_colored, height=35*(number_of_players + 1))

    st.text(f"Latest matches of: {boxes[0]['box']['eventName'][0]}")
    st.dataframe(results_df.sort_values(by=['UpdateDate'], ascending=False).head(10))
    