# TODO: Liigat: https://api.ussquash.com/resources/leagues?TopRecords=50&OrganizationId=10142&Admin=false&Status=0 --> & status 1 --> leagueid
# TODO: Liiga: https://api.ussquash.com/resources/leagues/results/606 --> scorecardid
# TODO: Scorecard: https://api.ussquash.com/resources/leagues/scorecards/live?id=133473

import datetime as dt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sn
import streamlit as st
from utils.extraction import load_tournaments, load_matches, load_rankings
from utils.general import add_bg_from_local, convert_df_to_csv
from pyinstrument import Profiler


profiler = Profiler()
profiler.start()


# Basic configurations.
pd.options.mode.chained_assignment = None  # default='warn'
st.set_page_config(
    page_title="Club Locker Data Analysis",
    page_icon="res/nikkiboxi.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={}
)


add_bg_from_local("res/squash_wall_dark95_blur3.jpg")








plt.style.use("ggplot")
colors = ["#BC9343", "#9B7A35", "#5D4B22", "#020202", "#E3021A"]
custom_palette_cmap = sn.blend_palette(
    colors=[
        (0.0008, 0.0008, 0.0008, 1),
        (0.89, 0.00, 0.102, 1),
        (0.737, 0.573, 0.26, 1),
    ],
    n_colors=100,
    as_cmap=True,
)
custom_palette = sn.blend_palette(
    colors=[
        (0.0008, 0.0008, 0.0008, 1),
        (0.89, 0.00, 0.102, 1),
        (0.737, 0.573, 0.26, 1),
    ],
    n_colors=100,
    as_cmap=False,
)
current_date = dt.datetime.now().date()

# Page header.
header_container = st.container()
header_container.image("res/legacy.png")
header_container.markdown("> [github.com/ilmarivikstrom/clublocker](https://github.com/ilmarivikstrom/clublocker)")
header_container.markdown("# Squash Finland Club Locker Data Analysis")

tournaments_df = load_tournaments()
matches_df = load_matches(tournaments_df)
rankings_df = load_rankings()

st.sidebar.image("res/legacy.png")
st.sidebar.download_button(
    label="Download raw tournament data as CSV",
    data=convert_df_to_csv(tournaments_df),
    file_name=f"tournaments_{str(current_date)}.csv",
    mime="text/csv",
)
st.sidebar.download_button(
    label="Download raw match data as CSV",
    data=convert_df_to_csv(matches_df),
    file_name=f"matches_{str(current_date)}.csv",
    mime="text/csv",
)

header_container.info(
    f"Tournament data covers {len(tournaments_df)} tournaments starting from {str(tournaments_df['StartDatePandas'].min().date())} and ending in {str(tournaments_df['StartDatePandas'].max().date())}."
)
header_container.info(
    f"Match data covers {len(matches_df)} matches starting from {str(matches_df['MatchDatePandas'].min().date())} and ending in {str(matches_df['MatchDatePandas'].max().date())}."
)
header_container.info(
    f"Only tournament matches are included. League matches are not included in the analysis."
)

header_container.markdown("---")


tournament_container = st.container()

tournament_container.markdown("## Tournament data")
tournament_container.markdown(
    "The data includes all tournaments that are (publicly) visible in Club Locker history of Finnish Squash Association. For clarity, all canceled tournaments are excluded from the dataset."
)
tournament_container.markdown("### Participation over time")
tournament_container.markdown(
    "Let's examine the general tournament participation over time:"
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
    order=3,
)
sn.regplot(
    data=tournaments_df.loc[tournaments_df["covid"] == "pre"].sort_values(
        "StartDatePandas"
    ),
    x="StartDateTimeStamp",
    y="NumPlayers",
    scatter=False,
    order=1,
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
tournament_container.markdown(
    "Data seems to suggest that a decreasing trend in tournament participation was in place already during pre-covid era. This is indicated by the slowly decreasing blue line. Summer breaks and lockdown periods are visible as temporal gaps in the data."
)


tournament_container.markdown("---")


match_container = st.container()

match_container.markdown("## Match data")
match_container.markdown(
    "Match data includes only matches played in tournaments. League matches are not included in the data yet."
)
match_container.markdown("### Match length distribution")
match_container.markdown(
    "It is expected that the number of rallies per match is not distributed in a Gaussian manner. This is assumed because the number of games in each match vary between 3 and 5. Each additional game adds a minimum of 11 points to the total number of rallies per match."
)
match_container.markdown("Let's see what the distribution looks like:")
fig, ax = plt.subplots()
fig.tight_layout()
ax.set_xlabel("Number of rallies")
ax.set_ylabel("Match count")
# HACK: Set the ylims so that the scatter and the pdf match visually.
ax.set_ylim([-10, 190])
sn.histplot(ax=ax, data=matches_df[["Rallies"]], binwidth=1, legend=False)
ax = ax.twinx()
ax.set_xlabel("Number of rallies")
ax.set_ylabel("Density")
# HACK: Set the ylims so that the scatter and the pdf match visually.
ax.set_ylim([-0.002, 0.038])
sn.kdeplot(
    ax=ax, data=matches_df, x="Rallies", bw_adjust=0.5, palette=custom_palette_cmap
)
match_container.pyplot(fig)


match_container.markdown(
    "Let's also see how the number of rallies correlate with the match length in minutes:"
)
fig, ax = plt.subplots()
ax.set_xlabel("Match duration (minutes)")
ax.set_ylabel("Number of rallies")
g = sn.scatterplot(
    data=matches_df.loc[matches_df["NumberOfGames"] >= 3],
    x="MatchDuration",
    y="Rallies",
    hue="NumberOfGames",
    alpha=0.7,
    palette=custom_palette_cmap,
)
g.set(xlim=(0, 90))
match_container.pyplot(fig)


match_container.markdown("Finally, here's a distribution view of the same phenomena:")
fig, ax = plt.subplots()
fig.tight_layout()
g = sn.kdeplot(
    data=matches_df.loc[matches_df["NumberOfGames"] >= 3],
    x="MatchDuration",
    hue="NumberOfGames",
    fill=True,
    alpha=0.5,
    palette=custom_palette_cmap,
)
g.set(xlim=(0, 90))
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
player_activity_container.markdown("### Player activity analysis")
player_activity_container.markdown("The most active players")
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
        ["matchid", "hPlayerName", "vPlayerName", "Score_Short", "Winner", "Rallies"]
    ]
)
player_container.caption(f"Found {len(search_results)} matches for player {name}")


player_container.markdown(
    "And here's the visualization of wins and losses of the selected player's matches:"
)
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
fig, ax = plt.subplots()
multiple_type = demographics_container.radio("Chart type", ("Blended", "Stacked"))
if multiple_type == "Stacked":
    multiple_type = "stack"
else:
    multiple_type = "layer"
bin_width = demographics_container.select_slider(
    "Specify the bin size", options=[1, 2, 5, 10, 15, 20], value=2
)
g = sn.histplot(
    data=rankings_df,
    x="age",
    hue="division",
    multiple=multiple_type,
    binwidth=bin_width,
)
g.set(xlim=(0, 90))
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
fig, ax = plt.subplots()
sn.scatterplot(
    data=rankings_df.loc[rankings_df["division"].isin(divisions)],
    x="age",
    y="ranking",
    hue="division",
    alpha=0.5,
)
ax.set_xlim(start_xlim, end_xlim)
demographics_container.pyplot(fig)

demographics_container.markdown("---")

new_container = st.container()
new_container.markdown("### Matches played in tournaments over years and months")
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
    cmap="YlGn",
    linecolor="white",
    square=False,
    fmt="d",
)
new_container.pyplot(fig)


profiler.stop()
profiler.print()