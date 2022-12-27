import datetime as dt
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sn
import streamlit as st
from pyinstrument import Profiler

# from dotenv import load_dotenv

from utils.extraction import (
    load_matches,
    load_rankings,
    load_tournaments,
    get_latest_pickle_date,
)
from utils.general import (
    caption_text,
    custom_css,
    convert_df_to_csv,
    hide_table_row_index,
)
from utils.styles import *

# profiler = Profiler()
# profiler.start()

# Dotenv
# load_dotenv(override=True)

# Set display_mode to either "dev" or "prod".
display_mode = os.getenv("DISPLAYMODE")
# If not set in env vars, force prod.
if display_mode == None:
    display_mode = "prod"

# Basic configurations
pd.options.mode.chained_assignment = None
st.set_page_config(
    page_title="Squashlytics",
    page_icon="res/nikkiboxi.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={},
)
skip_data_fetch = True

custom_css()
plt.style.use("ggplot")

# Get the starting datetime.
current_date = dt.datetime.now().date()


# Page header.
_, header_image_container, _ = st.columns([1, 4, 1])
header_image_container.image("res/court3.png", caption="ASB Squash Courts - ASB TPoint")
header_text_container = st.container()
header_text_container.title(
    """
    A Brief Adventure into Finnish Squash Tournament Data
    """
)

author_container = st.container()
author_container.markdown(
    """
    > Visit the repo [github.com/ilmarivikstrom/clublocker](https://github.com/ilmarivikstrom/clublocker)

    > Connect on [https://linkedin.com/in/ilmarivikstrom](https://linkedin.com/in/ilmarivikstrom)
    """
)

author_container.markdown("---")

introduction_container = st.container()
introduction_container.markdown(
    """
    # 1. Introduction
    In 2021, [Finnish Squash Association (FSA) reported](https://www.squash.fi/Hallitutkimus+2021) that the Finnish squash scene had experienced significant growth during the past three years. A year later, FSA presented [encouraging study results](https://www.squash.fi/Squashin+kiinnostus+kasvussa) about the increased interest in squash in Finland.
    
    The key takeaways from the articles are the following:
    - over **500,000** Finnish people are interested in squash in 2022
    - growth of **over 70%** compared to the previous years
    
    This growth is visible to any hobbyist that is looking to book courts. Rewinding the previous years, it is evident that squash courts are in higher demand today (Q4/2022) than in recent history. My personal experience suggests that truckloads of newcomers, in particular, are finding the courts and enjoying the sport. This phenomenon is very clear at least in Helsinki during primetime hours in Helsinki.
    
    > *"These results are great news for the sport, no?"*

    Well, yes!!

    > *Are we experiencing some kind of a squash renaissance? Are the dark days already behind us?*
    
    We don't know yet. While increased interest is a healthy signal, it does not paint us the whole view. There are many unanswered questions, like **can we see the growth in competitive squash as well?** The linked FSA articles did not consider the trends in competitive squash at all. I have not seen a single proper analysis where tournament statistics are being discussed thoroughly. To be frank, there aren't any good reasons why such an analysis has not been conducted. The data from all tournaments, matches, and league activities are publicly available from the FSA Club Locker portal. In this report, we are scraping the data from Club Locker and performing the analysis.
    
    This report attempts to showcase the open squash tournament data for the public. The following objectives have guided my work:
    - present the historical data in a human-readable format
    - find patterns and draw insights from the data
    - spread the insights and encourage discussion
    - take a step toward a more data-driven future and decision making

    ***Disclaimer: I have done my best to ensure the analysis is done properly without any major mistakes or misconclusions. However, such software bugs or misunderstandings may still exist in the following analysis.***

    #### Alright! With all of these out of the way, let's dive in.
    """
)
introduction_container.markdown("---")


loading_container = st.container()
loading_container.markdown(
    """
    # 2. Loading and pre-processing the Club Locker tournament data
    Before any analysis can take place, we need to fetch and pre-process fresh data from the Club Locker service. This happens automatically in the background, so you do not need to do anything.

    It should be noted, that **only tournament data is considered** in this study. This means that league matches, box league matches, etc., are omitted from the dataset.

    You can advance in the analysis only after the data has been loaded, so *please hold on tight while we get the things ready for you...*
    """
)

tournaments_df = load_tournaments(skip=skip_data_fetch)
matches_df = load_matches(skip=skip_data_fetch, tournaments_df=tournaments_df)
rankings_df = load_rankings(skip=skip_data_fetch)

loading_container.info(
    f"Tournament data is ready! The data covers **{len(tournaments_df)} tournaments** from {str(tournaments_df['StartDatePandas'].min().date())} until {str(tournaments_df['StartDatePandas'].max().date())}."
)
loading_container.info(
    f"Match data is ready! The data covers **{len(matches_df)} matches** from {str(matches_df['MatchDatePandas'].min().date())} until {str(matches_df['MatchDatePandas'].max().date())}."
)
loading_container.info(
    f"Ranking data is ready! The data covers **{len(rankings_df.loc[rankings_df['division'] == 'All Men'])} men** and **{len(rankings_df.loc[rankings_df['division'] == 'All Women'])} women**."
)
loading_container.success("⬇ All data has been fetched. Let's move on! ⬇")
loading_container.markdown("---")


st.sidebar.markdown(
    """
    # Table of Contents
    - [1. Introduction](#1-introduction)
    - [2. Loading and Pre-Processing the Club Locker Tournament Data](#2-loading-and-pre-processing-the-club-locker-tournament-data)
    - [3. Overview of the Tournament Data](#3-overview-of-the-tournament-data)
      - [3.1 First things first: some fun statistics](#3-1-first-things-first-some-fun-statistics)
      - [3.2 Down to business: Participation in squash tournaments over time](#3-2-down-to-business-participation-in-squash-tournaments-over-time)
    - [4. Overview of the player data](#4-overview-of-the-player-data)
      - [4.1 The most active players](#4-1-the-most-active-players)
      - [4.2 The toughest rivalries](#4-2-the-toughest-rivalries)
    - [5. Player demographics](#5-player-demographics)
      - [5.1 Age of the player base](#5-1-age-of-the-player-base)
      - [5.2 Player's age vs. ranking](#5-2-player-s-age-vs-ranking)

    ---
    """
)

st.sidebar.markdown(
    """
    #### Interested in the datasets? Download from here.
    """
)
st.sidebar.download_button(
    label="Tournament data",
    data=convert_df_to_csv(tournaments_df),
    file_name=f"tournaments_{str(get_latest_pickle_date('data/tournaments*'))}.csv",
    mime="text/csv",
)
st.sidebar.download_button(
    label="Match data",
    data=convert_df_to_csv(matches_df),
    file_name=f"matches_{str(get_latest_pickle_date('data/matches*'))}.csv",
    mime="text/csv",
)
st.sidebar.download_button(
    label="Ranking data",
    data=convert_df_to_csv(rankings_df),
    file_name=f"rankings_{str(get_latest_pickle_date('data/rankings*'))}.csv",
    mime="text/csv",
)


tournament_container = st.container()

tournament_container.markdown(
    f"""
    # 3. Overview of the tournament data

    In this section, we are taking a general look on the tournament data.

    #### 3.1 First things first: some fun statistics

    Club Locker history contains **{len(tournaments_df)}** tournaments and **{len(matches_df)}** matches. Here are some cool insights:
    
    - Total number of games: **{matches_df["NumberOfGames"].sum()}**
    - Total number of rallies: **{matches_df["Rallies"].sum()}**
    - Total time spent on court: **{matches_df["MatchDuration"].sum()}** minutes = **{int(matches_df["MatchDuration"].sum()/60)}** hours = **{round(matches_df["MatchDuration"].sum()/(60*24), 1)}** days
    - Average number of games in a match: **{round(matches_df["NumberOfGames"].mean(), 2)}**
    - Average number of rallies in a match: **{round(matches_df["Rallies"].mean(), 2)}**
    - Average match length: **{round(matches_df["MatchDuration"].mean(), 2)}** minutes
    - Average number of players in a tournament: **{round(tournaments_df["NumPlayers"].mean(), 2)}**

    There are plenty more insights that you can draw from the data. If you'd like to play around with the data, you can do so yourself. Please find the download links for the pre-processed datasets by expanding the menu to the left on this page.
    """
)

tournament_container.markdown(
    """
    #### 3.2 Down to business: Participation in squash tournaments over time

    The number of tournament participants is a great metric for gauging interest in competitive squash. Let's visualize the tournament participation by representing each tournament with a colored circle. The color signals if the tournament was held before or after the pandemic started.
    """
)
fig, ax = plt.subplots()
fig.tight_layout()
sn.scatterplot(
    data=tournaments_df.sort_values("StartDatePandas"),
    x="StartDateTimeStamp",
    y="NumPlayers",
    hue="covid",
    palette=[custom_palette[0], custom_palette[-1]],
)

sn.regplot(
    data=tournaments_df.sort_values("StartDatePandas"),
    x="StartDateTimeStamp",
    y="NumPlayers",
    scatter=False,
    order=2,
)
ax.set_xlabel("Tournament date")
ax.set_ylabel("Players in a tournament")
ax.xaxis.set_major_locator(mdates.YearLocator())
xticks = ax.get_xticks()
xticks_dates = [pd.to_datetime(dt.date.fromordinal(int(x))).date() for x in xticks]
xticks_dates = [x + pd.Timedelta(1, "d") if x.day == 31 else x for x in xticks_dates]
ax.set_xticklabels(xticks_dates)
for label in ax.get_xticklabels(which="major"):
    label.set(rotation=30, horizontalalignment="center", fontsize=8)
tournament_container.pyplot(fig)
tournament_container.markdown(
    caption_text("Figure 1", "Tournament participation pre- and post-covid."),
    unsafe_allow_html=True,
)

tournament_container.markdown(
    """
    Looking at Figure 1, we can see a few different things. The first clear observation is that the largest tournaments were held in the pre-covid era. When taking a bit more careful look at the data, we can see the quiet summer breaks and the lockdown months. If we exclude the lockdown periods, the density of the tournament calendar seems to be relatively the same for the whole history.
    
    The red line skewering the graph is a 2nd-order polynomial model fitted on the data. This model shows the general trend of tournament participation. The trend shows the harsh truth, which is that there has been a clear decreasing trend for a long time.
    """
)


tournament_container.markdown(
    f"""
    Let's plot the same tournament participation data in a way where it is easy to compare the same months of different years.
    """
)
fig, ax = plt.subplots()

tournament_players_months_weeks = (
    tournaments_df.groupby(by=["Month", "Year"])
    .sum()[["NumPlayers"]]
    .reset_index()
    .pivot("Year", "Month", "NumPlayers")
    .fillna(0)
    .astype(int)
)

sn.heatmap(
    tournament_players_months_weeks,
    linewidths=1,
    cmap=sn.color_palette("rocket_r", as_cmap=True),
    linecolor="white",
    square=False,
    fmt="d",
    annot=True,
)
tournament_container.pyplot(fig)
tournament_container.markdown(
    caption_text("Figure 2", "Heatmap of tournament participation."),
    unsafe_allow_html=True,
)
tournament_container.markdown(
    """

    """
)


number_top_tournaments = 15
tournament_container.markdown(
    f"""
    ---
    In the data we can see a few outliers. These are the tournaments that managed to draw the highest participation ever. Let's pick the top {number_top_tournaments} tournaments with the most participants in history and see what they were!
    """
)

top_highest_tournaments_df = tournaments_df.sort_values(
    by=["NumPlayers"], ascending=False
).head(number_top_tournaments)[["TournamentName", "Year", "NumPlayers", "covid"]]
tournament_container.markdown(hide_table_row_index(), unsafe_allow_html=True)

tournament_container.table(
    top_highest_tournaments_df.rename(
        columns={
            "TournamentName": "Tournament",
            "NumPlayers": "Players",
            "covid": "Covid",
        }
    ).style.background_gradient(cmap="Greens", low=0.5, subset=["Players"])
)
tournament_container.markdown(
    caption_text("Table 1", "Tournaments with highest participation."),
    unsafe_allow_html=True,
)

tournament_container.markdown(
    f"""
    A couple of insights from this table:
    - Out of these **{number_top_tournaments}** tournaments, **{len(top_highest_tournaments_df.loc[top_highest_tournaments_df["covid"] == "post"])}** tournaments took place post-pandemic.
    - National championships (juniors, masters and general) are drawing in a lot of participants.

    \\
    Alright, let's then look at the other end. These are the {number_top_tournaments} tournaments with the least participation!
    """
)

top_lowest_tournaments_df = tournaments_df.sort_values(
    by=["NumPlayers"], ascending=True
).head(number_top_tournaments)[["TournamentName", "Year", "NumPlayers", "covid"]]
tournament_container.table(
    top_lowest_tournaments_df.rename(
        columns={
            "TournamentName": "Tournament",
            "NumPlayers": "Players",
            "covid": "Covid",
        }
    ).style.background_gradient(cmap="Reds_r", high=0.5, subset=["Players"])
)
tournament_container.markdown(
    caption_text("Table 2", "Tournaments with lowest participation."),
    unsafe_allow_html=True,
)

tournament_container.markdown(
    f"""
    A couple of insights from this table as well:
    - Out of these **{number_top_tournaments}** tournaments, **{len(top_lowest_tournaments_df.loc[top_lowest_tournaments_df["covid"] == "post"])}** tournaments took place post-pandemic.
    - Most of these tournaments were held outside Uusimaa.
    - Some of these tournaments were small by design, e.g. qualifications for national teams, etc.
    """
)


tournament_container.markdown("---")


player_activity_container = st.container()
show_results = 25
player_activity_container.markdown("# 4. Overview of the player data")
player_activity_container.markdown(
    """
    Let's take a look at the data we have about the players who participate in the squash tournaments.
    """
)
player_activity_container.markdown(
    f"""
    #### 4.1 The most active players
    The tournaments cannot happen without an active base of competitive players. The rankings include hundreds and hundreds of competitive players, but it would be interesting to know who exactly are the players that participate the most. Here is a list of the top {show_results} active players in descending order!
    """
)


unique_player_names = list(
    set(matches_df["WinnerPlayer"].values.tolist())
    | set(matches_df["LoserPlayer"].values.tolist())
)

active_players_df = (
    pd.concat(
        [
            matches_df.groupby(by=["LoserPlayer"]).count().reset_index(names="Player"),
            matches_df.groupby(by=["WinnerPlayer"]).count().reset_index(names="Player"),
        ]
    )
    .groupby(by="Player")
    .sum()
    .sort_values(by="matchid", ascending=False)
    .reset_index()[["Player", "WinnerPlayer", "LoserPlayer"]]
)
active_players_df["TotalMatches"] = (
    active_players_df["WinnerPlayer"] + active_players_df["LoserPlayer"]
)
active_players_df[["WinnerPlayer", "LoserPlayer"]] = active_players_df[
    ["LoserPlayer", "WinnerPlayer"]
]

fig, ax = plt.subplots()
sn.barplot(
    data=active_players_df.head(show_results),
    x="TotalMatches",
    y="Player",
    palette=sn.color_palette("husl", show_results * 20),
)
ax.set_xlabel("Number of played matches")
ax.set_ylabel("Player name")

player_activity_container.pyplot(fig)
player_activity_container.markdown(
    caption_text(f"Figure 3", f"Top {show_results} most active players."),
    unsafe_allow_html=True,
)


player_activity_container.markdown(
    f"""
    #### 4.2 The toughest rivalries
    One of the best aspects of competitive squash is the formation of friendly rivalries when two relatively equally skilled players meet each other. Based on the players' activity and pure luck, a rivalrous matchup can happen surprisingly often. Here's a breakdown of the top {show_results} most common matchups that have taken place!
    """
)
common_matchups_df = (
    matches_df.groupby(by=["WinnerPlayer", "LoserPlayer"])
    .count()
    .sort_values(by="matchid", ascending=False)
    .reset_index(names=["Player1", "Player2"])[["Player1", "Player2", "matchid"]]
)
common_matchups_df["Matchup"] = common_matchups_df["Player1"].str.cat(
    common_matchups_df["Player2"], sep=" vs. "
)
fig, ax = plt.subplots()
sn.barplot(
    data=common_matchups_df.head(show_results),
    x="matchid",
    y="Matchup",
    palette=sn.color_palette("husl", show_results * 20),
)
ax.set_xlabel("Number of played matches")
ax.set_ylabel("Matchup")
player_activity_container.pyplot(fig)
player_activity_container.markdown(
    caption_text("Figure 4", f"Top {show_results} toughest rivalries."),
    unsafe_allow_html=True,
)

player_activity_container.markdown("---")


demographics_container = st.container()
demographics_container.markdown("# 5. Player demographics")
demographics_container.markdown("#### 5.1 Age of the player base")
MULTIPLE_TYPE = "stack"
bin_width = 2
# bin_width = demographics_container.select_slider(
#    "Specify the bin size", options=[1, 2, 5, 10, 15, 20], value=2
# )
hack_palette = [custom_palette[0], custom_palette[-1]]
fig, ax = plt.subplots()
sn.histplot(
    data=rankings_df.rename(columns={"division": "Category"}),
    x="age",
    hue="Category",
    multiple=MULTIPLE_TYPE,
    binwidth=bin_width,
    palette=hack_palette,
)
ax.set_xlim((0, 90))
ax.set_xlabel("Player age")
demographics_container.pyplot(fig)
demographics_container.markdown(
    caption_text("Figure 5", f"Age distribution of competitive players."),
    unsafe_allow_html=True,
)


demographics_container.markdown("#### 5.2 Player's age vs. ranking")
# divisions = demographics_container.multiselect(
#    "Filter players by division", ["All Men", "All Women"], ["All Men", "All Women"]
# )
divisions = ["All Men", "All Women"]
# start_xlim, end_xlim = demographics_container.select_slider(
#    "Specify the age range",
#    options=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90],
#    value=(0, 90),
# )
start_xlim, end_xlim = (0, 90)
hack_palette = [custom_palette[0], custom_palette[-1]]
fig, ax = plt.subplots()
sn.scatterplot(
    data=rankings_df.rename(columns={"division": "Category"}).loc[
        rankings_df.rename(columns={"division": "Category"})["Category"].isin(divisions)
    ],
    x="age",
    y="ranking",
    hue="Category",
    alpha=0.5,
    palette=hack_palette,
)
ax.set_xlim(start_xlim, end_xlim)
demographics_container.pyplot(fig)
demographics_container.markdown(
    caption_text("Figure 6", "Ranking as a function of age."), unsafe_allow_html=True
)

demographics_container.markdown("---")


# Hide the following unless in "dev" mode.
if display_mode != "prod":
    wip_container = st.container()
    wip_container.markdown("---")
    wip_container.markdown("# Everything below is under construction!")
    wip_container.markdown("---")
    wip_container.markdown("---")

    match_container = st.container()

    match_container.markdown("## Overview of the match data")
    match_container.markdown("")
    match_container.markdown("### Match length distribution")
    match_container.markdown("")
    fig, ax = plt.subplots()
    fig.tight_layout()
    ax.set_xlabel("Number of rallies")
    ax.set_ylabel("Match count")
    sn.histplot(
        ax=ax,
        data=matches_df,
        x="Rallies",
        hue="NumberOfGames",
        binwidth=1,
        multiple="stack",
        legend=True,
        palette=custom_palette_cmap,
    )
    match_container.pyplot(fig)

    match_container.markdown("")
    fig, ax = plt.subplots()
    ax.set_xlabel("Match duration (minutes)")
    ax.set_ylabel("Number of rallies")
    sn.scatterplot(
        data=matches_df,
        x="MatchDuration",
        y="Rallies",
        hue="NumberOfGames",
        alpha=0.2,
        palette=custom_palette_cmap,
        linewidth=0,
    )
    match_container.pyplot(fig)

    match_container.markdown("")
    fig, ax = plt.subplots()
    fig.tight_layout()
    sn.histplot(
        ax=ax,
        data=matches_df,
        x="MatchDuration",
        hue="NumberOfGames",
        binwidth=1,
        multiple="stack",
        legend=True,
        palette=custom_palette_cmap,
    )
    ax.set_xlabel("Match duration (minutes)")
    match_container.pyplot(fig)

    match_container.markdown("---")

    match_container.markdown("### Match length visualization for a selected tournament")
    selected_tournament = match_container.selectbox(
        "Select the tournament name",
        tournaments_df["TournamentName"].loc[tournaments_df["Type"] == "results"],
    )
    selected_tournament_id = tournaments_df.loc[
        tournaments_df["TournamentName"] == selected_tournament
    ]["TournamentID"].values[0]
    selected_matches = matches_df.loc[
        matches_df["TournamentID"] == selected_tournament_id
    ]
    match_container.markdown(
        f"Selected {len(selected_matches)} matches from {selected_tournament}"
    )
    fig, ax = plt.subplots()
    fig.tight_layout()
    ax.set_xlabel("Time")
    ax.set_ylabel("Number of Rallies")
    matches_subset = matches_df.loc[
        matches_df["TournamentID"] == selected_tournament_id
    ][["matchStart", "Rallies"]].dropna()
    matches_subset = matches_subset.loc[
        pd.to_datetime(matches_subset["matchStart"])
        > pd.to_datetime("01-01-2018T00:00:00.000Z")
    ]
    sn.scatterplot(
        x=pd.to_datetime(matches_subset["matchStart"]),
        y=matches_subset["Rallies"],
        hue=matches_subset["Rallies"],
        palette=custom_palette_cmap,
    )
    for label in ax.get_xticklabels(which="major"):
        label.set(rotation=30, horizontalalignment="center", fontsize=8)
    match_container.pyplot(fig)
    match_container.markdown("---")

    player_container = st.container()

    player_container.markdown(
        "### Individual player statistics based on tournament data"
    )
    unique_player_names = np.sort(
        pd.unique(matches_df[["vPlayerName", "hPlayerName"]].values.ravel("K"))
    )
    unique_player_names = np.concatenate((["Select a player"], unique_player_names))
    name = player_container.selectbox("", unique_player_names)
    search_results = matches_df.loc[
        matches_df["vPlayerName"].str.contains(name, case=False)
        | matches_df["hPlayerName"].str.contains(name, case=False)
    ]
    if name != "Select a player":
        search_results["Win"] = search_results["WinnerPlayer"] == name
        search_results = search_results.sort_values(by=["matchid"], ascending=False)
        player_container.markdown(f"Here's a tabular view of {name}'s matches:")
        player_container.markdown(hide_table_row_index(), unsafe_allow_html=True)

        player_container.table(
            search_results[
                [
                    "WinnerPlayer",
                    "LoserPlayer",
                    "Score_Short",
                    "Rallies",
                    "MatchDatePandas",
                    "TournamentName",
                ]
            ]
        )
        player_container.caption(f"Found {len(search_results)} matches for {name}")

        player_container.markdown(f"#### {name}'s wins and losses over time:")
        fig, ax = plt.subplots()
        fig.tight_layout()
        # HACK: Work around the palette bug when there's not enough categories:
        hack_palette = [custom_palette[0], custom_palette[-1]]
        if len(search_results["Win"].unique()) == 1:
            hack_palette = [custom_palette[int((len(custom_palette) - 1) / 2)]]
        sn.scatterplot(
            data=search_results,
            y="Rallies",
            x="MatchDatePandas",
            hue="Win",
            palette=hack_palette,
            legend=True,
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of rallies")
        for label in ax.get_xticklabels(which="major"):
            label.set(rotation=30, horizontalalignment="center", fontsize=8)
        player_container.pyplot(fig)

    player_container.markdown("---")

    new_container = st.container()
    new_container.markdown("### Tournament matches played over years and months")
    fig, ax = plt.subplots()

    tournaments_months_weeks = (
        tournaments_df.groupby(by=["Month", "Year"])
        .sum()[["NumMatches"]]
        .reset_index()
        .pivot("Year", "Month", "NumMatches")
        .fillna(0)
        .astype(int)
    )

    matches_months_weeks = (
        matches_df.groupby(by=["Month", "Weekday"])
        .count()[["MatchDuration"]]
        .reset_index()
        .pivot("Weekday", "Month", "MatchDuration")
        .fillna(0)
        .astype(int)
    )

    sn.heatmap(
        tournaments_months_weeks,
        linewidths=1,
        cmap=sn.color_palette("rocket_r", as_cmap=True),
        linecolor="white",
        square=False,
        fmt="d",
        annot=True,
    )
    new_container.pyplot(fig)

# profiler.stop()
# profiler.print()
