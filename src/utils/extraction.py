import datetime as dt
import json
from os import path

import pandas as pd
import pytz
import requests
import streamlit as st


def load_tournaments() -> pd.DataFrame:
    # Fetch and save tournaments, if needed.
    current_date = dt.datetime.now().date()
    if not path.exists(f"data/tournaments_{str(current_date)}.pkl"):
        with st.spinner(
            "Loading tournament data from Club Locker, please be patient..."
        ):
            _fetch_and_save_tournaments(
                file_name=f"tournaments_{str(current_date)}.pkl"
            )
    tournaments_df_dirty = _load_pickle(
        file_name=f"tournaments_{str(current_date)}.pkl"
    )
    tournaments_df_dirty["StartDatePandas"] = pd.to_datetime(
        tournaments_df_dirty["StartDate"]
    )
    tournaments_df_dirty = tournaments_df_dirty[
        (tournaments_df_dirty["NumMatches"] > 0)
        & (tournaments_df_dirty["NumPlayers"] > 0)
    ]
    tournaments_df = _preprocess_tournaments(tournaments_df_dirty)
    return tournaments_df


def load_matches(tournaments_df: pd.DataFrame) -> pd.DataFrame:
    # Fetch and save tournament matches, if needed.
    current_date = dt.datetime.now().date()
    if not path.exists(f"data/matches_{str(current_date)}.pkl"):
        with st.spinner(
            "Loading match data from Club Locker. This can take a while, please be patient..."
        ):
            _fetch_and_save_tournament_matches(
                tournaments_df, file_name=f"matches_{str(current_date)}.pkl"
            )
    matches_df_dirty = _load_pickle(file_name=f"matches_{str(current_date)}.pkl")
    matches_df = _preprocess_matches(matches_df_dirty)
    return matches_df


def load_rankings() -> pd.DataFrame:
    # Fetch and save ranking data, if needed.
    current_date = dt.datetime.now().date()
    if not path.exists(f"data/rankings_{str(current_date)}.pkl"):
        with st.spinner("Loading ranking data from Club Locker, please be patient..."):
            _fetch_and_save_rankings(file_name=f"rankings_{str(current_date)}.pkl")
    rankings_df_dirty = _load_pickle(file_name=f"rankings_{str(current_date)}.pkl")
    rankings_df = _preprocess_rankings(rankings_df_dirty)
    return rankings_df


def _preprocess_tournaments(tournaments_df_dirty: pd.DataFrame) -> pd.DataFrame:
    # Tournament data preprocessing.
    start_dates = pd.to_datetime(tournaments_df_dirty["StartDate"].values.tolist())
    covid = []
    for start_date in start_dates:
        if start_date < pd.to_datetime("2020-03-01"):
            covid.append("pre")
        else:
            covid.append("post")
    tournaments_df_dirty["covid"] = covid
    tournaments_df_dirty["StartDateTimeStamp"] = pd.to_datetime(
        tournaments_df_dirty["StartDate"]
    )
    tournaments_df_dirty["StartDateTimeStamp"] = tournaments_df_dirty[
        "StartDateTimeStamp"
    ].map(dt.datetime.toordinal)
    tournaments_df_dirty["Weekday"] = [
        x.weekday() for x in tournaments_df_dirty["StartDatePandas"]
    ]
    tournaments_df_dirty["Year"] = [
        x.year for x in tournaments_df_dirty["StartDatePandas"]
    ]
    tournaments_df_dirty["Month"] = [
        x.month for x in tournaments_df_dirty["StartDatePandas"]
    ]
    tournaments_df_dirty["Week"] = [
        x.week for x in tournaments_df_dirty["StartDatePandas"]
    ]
    tournaments_df_dirty.sort_values(by=["StartDatePandas"], ascending=True, inplace=True)
    tournaments_df = tournaments_df_dirty
    return tournaments_df


@st.experimental_memo
def _preprocess_rankings(rankings_df_dirty: pd.DataFrame) -> pd.DataFrame:
    rankings_df = rankings_df_dirty
    return rankings_df


@st.experimental_memo
def _preprocess_matches(matches_df_dirty):
    # Match data preprocessing.
    matches_df_dirty["hPlayerName"] = matches_df_dirty["hPlayerName"].str.split(",").str[::-1].str.join(",").str.replace(",", " ")
    matches_df_dirty["vPlayerName"] = matches_df_dirty["vPlayerName"].str.split(",").str[::-1].str.join(",").str.replace(",", " ")
    matches_df_dirty["MatchDatePandas"] = pd.to_datetime(matches_df_dirty["MatchDate"])
    matches_df_dirty["Game1"] = (
        matches_df_dirty["wset1"] + matches_df_dirty["oset1"]
    ).fillna(0)
    matches_df_dirty["Game2"] = (
        matches_df_dirty["wset2"] + matches_df_dirty["oset2"]
    ).fillna(0)
    matches_df_dirty["Game3"] = (
        matches_df_dirty["wset3"] + matches_df_dirty["oset3"]
    ).fillna(0)
    matches_df_dirty["Game4"] = (
        matches_df_dirty["wset4"] + matches_df_dirty["oset4"]
    ).fillna(0)
    matches_df_dirty["Game5"] = (
        matches_df_dirty["wset5"] + matches_df_dirty["oset5"]
    ).fillna(0)
    matches_df_dirty["NumberOfGames"] = (
        (matches_df_dirty[["Game1", "Game2", "Game3", "Game4", "Game5"]] != 0)
        .astype(int)
        .sum(axis=1)
    )
    matches_df_dirty["Game1DurationSecs"] = pd.to_datetime(
        matches_df_dirty["gameDuration1"]
    ) - dt.datetime.fromtimestamp(0, pytz.utc)
    matches_df_dirty["Game2DurationSecs"] = pd.to_datetime(
        matches_df_dirty["gameDuration2"]
    ) - dt.datetime.fromtimestamp(0, pytz.utc)
    matches_df_dirty["Game3DurationSecs"] = pd.to_datetime(
        matches_df_dirty["gameDuration3"]
    ) - dt.datetime.fromtimestamp(0, pytz.utc)
    matches_df_dirty["Game4DurationSecs"] = pd.to_datetime(
        matches_df_dirty["gameDuration4"]
    ) - dt.datetime.fromtimestamp(0, pytz.utc)
    matches_df_dirty["Game5DurationSecs"] = pd.to_datetime(
        matches_df_dirty["gameDuration5"]
    ) - dt.datetime.fromtimestamp(0, pytz.utc)
    matches_df_dirty["MatchDuration"] = pd.to_datetime(
        matches_df_dirty["matchEnd"]
    ) - pd.to_datetime(matches_df_dirty["matchStart"])
    matches_df_dirty = matches_df_dirty.loc[
        matches_df_dirty["MatchDuration"] < pd.Timedelta(2, "h")
    ]
    matches_df_dirty = matches_df_dirty.loc[
        matches_df_dirty["MatchDuration"] > pd.Timedelta(4, "m")
    ]
    matches_df_dirty["MatchDuration"] = (
        matches_df_dirty["MatchDuration"].astype("timedelta64[m]").astype(int)
    )
    matches_df_dirty["Rallies"] = (
        matches_df_dirty[
            [
                "wset1",
                "oset1",
                "wset2",
                "oset2",
                "wset3",
                "oset3",
                "wset4",
                "oset4",
                "wset5",
                "oset5",
            ]
        ]
        .dropna()
        .sum(axis=1)
    )
    matches_df_dirty = matches_df_dirty.loc[
        (matches_df_dirty["matchid"] > 1000000)
        & (matches_df_dirty["Rallies"] > 20)
        & (matches_df_dirty["NumberOfGames"] >= 3)
        & (matches_df_dirty["NumberOfGames"] <= 5)
    ]
    matches_df_dirty["WinnerPlayer"] = (
        matches_df_dirty["vPlayerName"]
        .loc[matches_df_dirty["Winner"] == "V"]
        .dropna()
        .combine_first(
            matches_df_dirty["hPlayerName"]
            .loc[matches_df_dirty["Winner"] == "H"]
            .dropna()
        )
    )
    matches_df_dirty["LoserPlayer"] = (
        matches_df_dirty["vPlayerName"]
        .loc[matches_df_dirty["Winner"] == "H"]
        .dropna()
        .combine_first(
            matches_df_dirty["hPlayerName"]
            .loc[matches_df_dirty["Winner"] == "V"]
            .dropna()
        )
    )
    matches_df_dirty = matches_df_dirty.dropna(subset=["vPlayerName", "hPlayerName"])
    matches_df_dirty["Weekday"] = [
        x.weekday() for x in matches_df_dirty["MatchDatePandas"]
    ]
    matches_df_dirty["Year"] = [x.year for x in matches_df_dirty["MatchDatePandas"]]
    matches_df_dirty["Month"] = [x.month for x in matches_df_dirty["MatchDatePandas"]]
    matches_df_dirty["Week"] = [x.week for x in matches_df_dirty["MatchDatePandas"]]
    matches_df_dirty.sort_values(by=["MatchDatePandas"], ascending=True, inplace=True)
    matches_df = matches_df_dirty
    return matches_df


def _fetch_and_save_tournaments(file_name: str) -> None:
    tournaments_list = []
    tournament_types = {"scheduled": 1, "results": 3}
    for tournament_type in tournament_types.items():
        try:
            response = requests.get(
                url=f"https://api.ussquash.com/resources/tournaments?TopRecords=500&ngbId=10142&OrganizerType=1&Sanctioned=1&Status={tournament_type[1]}",
                timeout=10,
            )
            tournaments_js = json.loads(response.content)
            for tournament_js in tournaments_js:
                tournament_js["Type"] = tournament_type[0]
                tournaments_list.append(tournament_js)
        except requests.exceptions.Timeout:
            print("TODO: Handle timeout better.")
    tournaments_df = pd.DataFrame(tournaments_list, columns=tournaments_list[0].keys())
    tournaments_df.to_pickle(f"data/{file_name}")


def _fetch_and_save_tournament_matches(
    tournaments_df: pd.DataFrame, file_name: str
) -> None:
    results_df = tournaments_df
    dates_ids = list(
        zip(
            results_df["TournamentID"].values.tolist(),
            results_df["StartDate"].values.tolist(),
            results_df["EndDate"].values.tolist(),
        )
    )
    matches_list = []
    index = 0
    progress_bar = st.progress(0)
    for tournament in dates_ids:
        date_range_list = [
            str(x.date()) for x in pd.date_range(tournament[1], tournament[2])
        ]
        for date in date_range_list:
            try:
                response = requests.get(
                    url=f"https://api.ussquash.com/resources/res/trn/live_matrix?date={date}&tournamentId={tournament[0]}",
                    timeout=10,
                )
                matches_js = json.loads(response.content)
                for match_js in matches_js:
                    if len(match_js) > 1:
                        match_js["TournamentID"] = tournament[0]
                        matches_list.append(match_js)
            except requests.exceptions.Timeout:
                print("TODO: Handle timeout better.")
        print(
            f"Fetched matches from tournament {tournament[0]}. Total matches loaded: {len(matches_list)}"
        )
        index += 1
        progress_bar.progress(index / len(dates_ids))
    matches_df_dirty = pd.DataFrame(matches_list, columns=matches_list[0].keys())
    matches_df_dirty = matches_df_dirty.drop_duplicates(subset="matchid", keep="first")
    matches_df_dirty.to_pickle(f"data/{file_name}")


def _fetch_and_save_rankings(file_name: str) -> None:
    ranking_urls = [
        "https://api.ussquash.com/resources/rankings/9/current?divisions=2",
        "https://api.ussquash.com/resources/rankings/9/current?divisions=1",
    ]
    rankings_list = []
    for ranking_url in ranking_urls:
        for page_number in range(1, 20):
            ranking_url_with_page_number = ranking_url + f"&pageNumber={page_number}"
            try:
                response = requests.get(url=ranking_url_with_page_number, timeout=10)
                rankings_js = json.loads(response.content)
                if len(rankings_js) == 0:
                    break
                for ranking_js in rankings_js:
                    rankings_list.append(ranking_js)
            except requests.exceptions.Timeout:
                print("TODO: Handle timeout better.")
    rankings_df = pd.DataFrame(rankings_list, columns=rankings_list[0].keys())
    rankings_df.to_pickle(f"data/{file_name}")


@st.experimental_memo
def _load_pickle(file_name: str) -> pd.DataFrame:
    pickle = pd.read_pickle(f"data/{file_name}")
    return pickle
