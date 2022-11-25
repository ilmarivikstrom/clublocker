import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sn
import streamlit as st
from pyinstrument import Profiler

from utils.extraction import load_matches, load_rankings, load_tournaments
from utils.general import add_bg_from_local, convert_df_to_csv
from utils.styles import *

profiler = Profiler()
profiler.start()

# Basic configurations
pd.options.mode.chained_assignment = None
st.set_page_config(
    page_title="Club Locker Data Analysis",
    page_icon="res/nikkiboxi.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={},
)
add_bg_from_local("res/squash_wall_dark95_blur3.jpg")
plt.style.use("ggplot")

# Get the starting datetime.
current_date = dt.datetime.now().date()

# Page header.
header_container = st.container()
header_container.image("res/legacy.png")
header_container.markdown(
    "> Visit [github.com/ilmarivikstrom/clublocker](https://github.com/ilmarivikstrom/clublocker)"
)
header_container.markdown(
    "> Connect on [https://linkedin.com/in/ilmarivikstrom](https://linkedin.com/in/ilmarivikstrom)"
)

header_container.markdown("# Squash Finland Club Locker Data Analysis")

tournaments_df = load_tournaments()
matches_df = load_matches(tournaments_df)
rankings_df = load_rankings()

header_container.info(
    f"Tournament data covers **{len(tournaments_df)}** tournaments starting from {str(tournaments_df['StartDatePandas'].min().date())} and ending in {str(tournaments_df['StartDatePandas'].max().date())}. Only tournament matches are included. League matches are not included in the analysis."
)
header_container.info(
    f"Match data covers **{len(matches_df)} matches** starting from {str(matches_df['MatchDatePandas'].min().date())} and ending in {str(matches_df['MatchDatePandas'].max().date())}."
)
header_container.info(
    f"Ranking data covers **{len(rankings_df.loc[rankings_df['division'] == 'All Men'])} men** and **{len(rankings_df.loc[rankings_df['division'] == 'All Women'])} women**."
)

header_container.markdown("---")

sb_col1, sb_col2, sb_col3 = st.sidebar.columns(3)
sb_col1.markdown("### Tournament data")
sb_col1.download_button(
    label="⬇️ Download ⬇️",
    data=convert_df_to_csv(tournaments_df),
    file_name=f"tournaments_{str(current_date)}.csv",
    mime="text/csv",
)
sb_col2.markdown("### Match data")
sb_col2.download_button(
    label="⬇️ Download ⬇️",
    data=convert_df_to_csv(matches_df),
    file_name=f"matches_{str(current_date)}.csv",
    mime="text/csv",
)
sb_col3.markdown("### Ranking data")
sb_col3.download_button(
    label="⬇️ Download ⬇️",
    data=convert_df_to_csv(rankings_df),
    file_name=f"rankings_{str(current_date)}.csv",
    mime="text/csv",
)


tournament_container = st.container()

tournament_container.markdown("## Tournament data")
tournament_container.markdown(
    "The data includes all tournaments that are (publicly) visible in Club Locker history of Finnish Squash Association. For clarity, all canceled tournaments are excluded from the dataset."
)
tournament_container.markdown("### Participation over time")
tournament_container.markdown("")
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
    order=3,
)
ax.set_xlabel("Date")
ax.set_ylabel("Number of players in tournament")
ax.xaxis.set_major_locator(mdates.YearLocator())
xticks = ax.get_xticks()
xticks_dates = [pd.to_datetime(dt.date.fromordinal(int(x))).date() for x in xticks]
xticks_dates = [x + pd.Timedelta(1, "d") if x.day == 31 else x for x in xticks_dates]
ax.set_xticklabels(xticks_dates)
for label in ax.get_xticklabels(which="major"):
    label.set(rotation=30, horizontalalignment="center", fontsize=8)
tournament_container.pyplot(fig)


tournament_container.dataframe(tournaments_df.sort_values(by=["NumPlayers"], ascending=False).head(10)[["TournamentName", "Year", "Month", "NumPlayers", "covid"]], use_container_width=True)


tournament_container.markdown("---")


match_container = st.container()

match_container.markdown("## Match data")
match_container.markdown("")
match_container.markdown("### Match length distribution")
match_container.markdown("")
match_container.markdown("Let's see what the distribution looks like:")
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


match_container.markdown(
    "Let's also see how the number of rallies correlate with the match length in minutes:"
)
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

match_container.markdown("Finally, here's a distribution view of the same phenomena:")
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
selected_matches = matches_df.loc[matches_df["TournamentID"] == selected_tournament_id]
match_container.markdown(
    f"Selected {len(selected_matches)} matches from {selected_tournament}"
)
fig, ax = plt.subplots()
fig.tight_layout()
ax.set_xlabel("Time")
ax.set_ylabel("Number of Rallies")
matches_subset = matches_df.loc[matches_df["TournamentID"] == selected_tournament_id][
    ["matchStart", "Rallies"]
].dropna()
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


player_activity_container = st.container()
fig, ax = plt.subplots()
player_activity_container.markdown("### Player activity analysis")
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

show_results = 15
sn.barplot(
    data=active_players_df.head(show_results),
    x="TotalMatches",
    y="Player",
    palette=sn.color_palette("husl", show_results * 20),
)
ax.set_xlabel("Number of matches played")
ax.set_ylabel("Player name")

player_activity_container.markdown("WIP")
player_activity_container.pyplot(fig)


player_activity_container.markdown("The most common matchups")
fig, ax = plt.subplots()
common_matchups_df = (
    matches_df.groupby(by=["WinnerPlayer", "LoserPlayer"])
    .count()
    .sort_values(by="matchid", ascending=False)
    .reset_index(names=["Player1", "Player2"])[["Player1", "Player2", "matchid"]]
)
common_matchups_df["Matchup"] = common_matchups_df["Player1"].str.cat(
    common_matchups_df["Player2"], sep=" vs. "
)
sn.barplot(
    data=common_matchups_df.head(show_results),
    x="matchid",
    y="Matchup",
    palette=sn.color_palette("husl", show_results * 20),
)
ax.set_xlabel("Number of matchups")
ax.set_ylabel("Players")
player_activity_container.pyplot(fig)

player_activity_container.markdown("---")


player_container = st.container()

player_container.markdown("### Individual player statistics based on tournament data")
unique_player_names = np.sort(
    pd.unique(matches_df[["vPlayerName", "hPlayerName"]].values.ravel("K"))
)
name = player_container.selectbox("Select a player", unique_player_names)
search_results = matches_df.loc[
    matches_df["vPlayerName"].str.contains(name, case=False)
    | matches_df["hPlayerName"].str.contains(name, case=False)
]
search_results["Win"] = search_results["WinnerPlayer"] == name
search_results = search_results.sort_values(by=["matchid"], ascending=False)
player_container.markdown("Here's a tabular view of the selected player:")
player_container.dataframe(
    search_results[
        ["WinnerPlayer", "LoserPlayer", "Score_Short", "Rallies", "MatchDatePandas"]
    ]
)
player_container.caption(f"Found {len(search_results)} matches for player {name}")


player_container.markdown("#### Wins and losses for the selected player:")
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
)
ax.set_xlabel("Date")
ax.set_ylabel("Number of rallies")
for label in ax.get_xticklabels(which="major"):
    label.set(rotation=30, horizontalalignment="center", fontsize=8)
player_container.pyplot(fig)

player_container.markdown("---")


demographics_container = st.container()
demographics_container.markdown("### Player demographics")
demographics_container.markdown("Age breakdown")
MULTIPLE_TYPE = demographics_container.radio("Chart type", ("Stacked", "Blended"))
if MULTIPLE_TYPE == "Stacked":
    MULTIPLE_TYPE = "stack"
else:
    MULTIPLE_TYPE = "layer"
bin_width = demographics_container.select_slider(
    "Specify the bin size", options=[1, 2, 5, 10, 15, 20], value=2
)
hack_palette = [custom_palette[0], custom_palette[-1]]
fig, ax = plt.subplots()
sn.histplot(
    data=rankings_df,
    x="age",
    hue="division",
    multiple=MULTIPLE_TYPE,
    binwidth=bin_width,
    palette=hack_palette,
)
ax.set_xlim((0, 90))
ax.set_xlabel("Player age")
demographics_container.pyplot(fig)


demographics_container.markdown("Ranking as a function of age")
divisions = demographics_container.multiselect(
    "Filter players by division", ["All Men", "All Women"], ["All Men", "All Women"]
)
start_xlim, end_xlim = demographics_container.select_slider(
    "Specify the age range",
    options=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90],
    value=(0, 90),
)
hack_palette = [custom_palette[0], custom_palette[-1]]
fig, ax = plt.subplots()
sn.scatterplot(
    data=rankings_df.loc[rankings_df["division"].isin(divisions)],
    x="age",
    y="ranking",
    hue="division",
    alpha=0.5,
    palette=hack_palette,
)
ax.set_xlim(start_xlim, end_xlim)
demographics_container.pyplot(fig)

demographics_container.markdown("---")

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
    cmap=custom_palette_cmap1,
    linecolor="white",
    square=False,
    fmt="d",
    annot=True,
)
new_container.pyplot(fig)


profiler.stop()
profiler.print()
