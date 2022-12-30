import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sn
import streamlit as st
from types import ModuleType

import config
from streamlit_multipage import MultiPage
from utils.extraction import (
    get_latest_pickle_date,
    load_matches,
    load_rankings,
    load_tournaments,
)
from utils.general import (
    caption_text,
    color_covid,
    convert_df_to_csv,
    custom_css,
    hide_table_row_index,
)
from utils.styles import *

# Display mode either "dev" or "prod" from config.
display_mode = config.display["mode"]

# Basic configurations
pd.options.mode.chained_assignment = None
st.set_page_config(
    page_title=config.display["main_title"],
    page_icon="res/nikkiboxi.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={},
)


def data_analysis(st: ModuleType, **state: dict):
    custom_css(background_path="res/neon_court2.png")
    plt.style.use("ggplot")

    # Page header.
    _, header_image_container, _ = st.columns([1, 4, 1])
    header_image_container.image(
        "res/court3.png", caption="Imagery: ASB TPoint Squash Courts"
    )
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

        > For the "Player vs. Player Analyzer", open sidebar and navigate there using the dropdown menu.
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
        
        This growth is visible to any hobbyist that is looking to book courts. Rewinding the previous years, it is evident that squash courts are in higher demand today (Q4/2022) than in recent history. My personal experience suggests that truckloads of newcomers, in particular, are finding the courts and enjoying the sport. This phenomenon is very clear at least in Helsinki during primetime hours.
        
        > *"These results are great news for the sport, no?"*

        Well, yes!!

        > *"Are we experiencing some kind of a squash renaissance? Are the dark days already behind us?"*
        
        We don't know yet. While increased interest is a healthy signal, it does not paint us the whole view. There are many unanswered questions, like **can we see the growth in competitive squash as well?** The linked FSA articles did not consider the trends in competitive squash at all. I have not seen a single proper analysis where tournament statistics are being discussed thoroughly. To be frank, there aren't any good reasons why such an analysis has not been conducted. The data from all tournaments, matches, and league activities are publicly available from the FSA Club Locker portal. In this report, we are scraping the data from Club Locker and performing the analysis.
        
        This report attempts to showcase the open squash tournament data for the public. The following objectives have guided my work:
        - present the historical data in a human-readable format
        - find patterns and draw insights from the data
        - spread the insights and encourage discussion
        - take a step toward a more data-driven future and decision making
        """
    )
    introduction_container.info(
        "Disclaimer: I have done my best to ensure the analysis is done properly without any major mistakes or misconclusions. However, such software bugs or misunderstandings may still exist in the following analysis."
    )
    introduction_container.markdown(
        "#### Alright! With all of these out of the way, let's dive in."
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

    tournaments_df = load_tournaments(skip=config.data["skip_fetch"])
    matches_df = load_matches(
        skip=config.data["skip_fetch"], tournaments_df=tournaments_df
    )
    rankings_df = load_rankings(skip=config.data["skip_fetch"])

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
        - [5. Demographics](#5-demographics)
          - [5.1 Age of the player base](#5-1-age-of-the-player-base)
          - [5.2 Player's age vs. ranking](#5-2-player-s-age-vs-ranking)
        - [6. Overview of the match data](#6-overview-of-the-match-data)
          - [6.1 Games, rallies and minutes in matches](#6-1-games-rallies-and-minutes-in-matches)
        - [7. The End](#7-the-end)
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
        palette=custom_palette_3,
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
    xticks_dates = [
        x + pd.Timedelta(1, "d") if x.day == 31 else x for x in xticks_dates
    ]
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
        )
        .style.background_gradient(cmap="Greens", low=0.5, subset=["Players"])
        .applymap(color_covid)
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
        )
        .style.background_gradient(cmap="Reds_r", high=0.5, subset=["Players"])
        .applymap(color_covid)
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
    show_results = 20
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

    active_players_df = (
        pd.concat(
            [
                matches_df.groupby(by=["LoserPlayer"])
                .count()
                .reset_index(names="Player"),
                matches_df.groupby(by=["WinnerPlayer"])
                .count()
                .reset_index(names="Player"),
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
    player_activity_container.markdown(
        """
        Many of the toughest rivalries seem to happen in categories where there are limited number of players. These categories can be certain junior age groups or senior age groups. Some of the most common matchups are between players who represent the same squash club.
        """
    )

    player_activity_container.markdown("---")

    demographics_container = st.container()
    demographics_container.markdown(
        """
        # 5. Demographics
        So far we have learned about some general statistics about tournaments, which players are the most active and what are the most common matchups. It is now time to zoom out and look at the whole competitive player base.
        """
    )
    bin_width = 2
    demographics_container.markdown(
        f"""
        #### 5.1 Age of the player base
        Squash is a sport for all ages. Due to that, there are active competitive players in almost all imaginable age groups. Let's see what is the age distribution in competitive squash players. Each bar represents a span of {bin_width} years, e.g. all players between 32 and 34 years.
        """
    )
    MULTIPLE_TYPE = "stack"
    fig, ax = plt.subplots()
    sn.histplot(
        data=rankings_df.rename(columns={"division": "Category"}),
        x="age",
        hue="Category",
        multiple=MULTIPLE_TYPE,
        binwidth=bin_width,
        palette=custom_palette_3,
    )
    ax.set_xlim((0, 90))
    ax.set_xlabel("Player age")
    ax.set_ylabel("Player count")
    demographics_container.pyplot(fig)
    demographics_container.markdown(
        caption_text("Figure 5", f"Age distribution of competitive players."),
        unsafe_allow_html=True,
    )
    demographics_container.markdown(
        f"""
        There's a few clear things we can see in this stacked bar chart. With a couple of exceptions, there seem to be significantly more men players in almost all age groups. Juniors between 10 and 20 years in age dominate the chart, which is expected. There is a huge drop off between 20 to 42, while the 42 to 64 year olds represents an age group with considerable depth.
        """
    )

    demographics_container.markdown(
        f"""
        #### 5.2 Player's age vs. ranking
        As squash is a physically demanding sport, it would make sense that the players' physical development reflects in the rankings as well. While it is possible for anyone to improve their physical condition in any age, there is a correlation between individual's age and their physical condition. With this in mind, let's see how our competitive players of different ages show up in the rankings.
        """
    )
    divisions = ["All Men", "All Women"]
    demographics_subplot_column1_container, demographics_subplot_column2_container = st.columns(2)
    start_xlim, end_xlim = (0, 90)
    fig, ax = plt.subplots()
    sn.scatterplot(
        data=rankings_df.rename(columns={"division": "Category", "age": "Player age", "ranking": "Ranking"}).loc[
            rankings_df.rename(columns={"division": "Category", "age": "Player age", "ranking": "Ranking"})["Category"] == divisions[0]
        ],
        x="Player age",
        y="Ranking",
        hue="Category",
        alpha=0.5,
        palette=[custom_palette_3[0]],
    )
    ax.set_xlim(start_xlim, end_xlim)
    demographics_subplot_column1_container.pyplot(fig)
    demographics_subplot_column1_container.markdown(
        caption_text("Figure 6", "Ranking as a function of age in men."),
        unsafe_allow_html=True,
    )

    start_xlim, end_xlim = (0, 90)
    fig, ax = plt.subplots()
    sn.scatterplot(
        data=rankings_df.rename(columns={"division": "Category", "age": "Player age", "ranking": "Ranking"}).loc[
            rankings_df.rename(columns={"division": "Category", "age": "Player age", "ranking": "Ranking"})["Category"] == divisions[1]
        ],
        x="Player age",
        y="Ranking",
        hue="Category",
        alpha=0.5,
        palette=[custom_palette_3[1]],
    )
    ax.set_xlim(start_xlim, end_xlim)
    demographics_subplot_column2_container.pyplot(fig)
    demographics_subplot_column2_container.markdown(
        caption_text("Figure 7", "Ranking as a function of age in women."),
        unsafe_allow_html=True,
    )

    demographics_contd_container = st.container()


    demographics_contd_container.markdown(
        f"""
        It is cool to see, that the development during junior years is so pronounced in the chart. There is a similar trend in the other end: the men's ranking (in particular) seems to plummet in players that are older than 60 years.

        The top players seem to represent a wide age group. For men, the top players are between 20 and 50 years old, while the top women players are between 16 and 50 years old.
        """
    )
    demographics_contd_container.markdown("---")

    match_container = st.container()

    match_container.markdown(
        f"""
        # 6. Overview of the match data
        There are probably a million ways of studying the Club Locker data. For this report, we can only do a few. In the next section, we are going to briefly touch the relatively uncovered match data.
        """
    )
    match_container.markdown("")
    match_container.markdown(
        f"""
        #### 6.1 Games, rallies and minutes in matches
        In the beginning we learned about total number of matches played, total number of rallies, and so on. There are mysteries to uncover, for example, we still do not have a clue about how many 5-game matches are played compared to 3-game matches. Let's plot the data over "total number of rallies", and see what's up.
        """
    )
    match_container.markdown("")
    fig, ax = plt.subplots()
    fig.tight_layout()
    ax.set_xlabel("Number of rallies")
    ax.set_ylabel("Match count")
    sn.histplot(
        ax=ax,
        data=matches_df.rename(
            columns={
                "NumberOfGames": "Games",
            }
        ),
        x="Rallies",
        hue="Games",
        binwidth=1,
        multiple="stack",
        legend=True,
        palette=custom_palette_3,
    )
    ax.set_xlim(20, 120)
    match_container.pyplot(fig)
    match_container.markdown(
        caption_text("Figure 8", "Games and rallies over the complete match dataset."),
        unsafe_allow_html=True,
    )

    match_container.markdown(
        f"""
        Clearly, the majority of matches are 3-game matches with around 50 rallies in total, while the most common 4-game match ends in 73 rallies. There are significantly less 5-game matches, with the longest being around 120 rallies long. Interesting!

        Alright Captain Obvious, we have seen that if you have more games, you also have more rallies. What about the match length in minutes? Well:
        """
    )
    fig, ax = plt.subplots()
    ax.set_xlabel("Match duration (minutes)")
    ax.set_ylabel("Number of rallies")
    sn.scatterplot(
        data=matches_df.rename(
            columns={
                "NumberOfGames": "Games",
            }
        ),
        x="MatchDuration",
        y="Rallies",
        hue="Games",
        alpha=0.15,
        palette=custom_palette_3,
        linewidth=0,
    )
    ax.set_xlim(-5, 90)
    match_container.pyplot(fig)
    match_container.markdown(
        caption_text("Figure 9", "Games and rallies as a function of match duration."),
        unsafe_allow_html=True,
    )

    match_container.markdown(
        f"""
        This time we are looking at a scatter plot. The darker the spot on the plot, the more overlapping data points there are.
        
        The data points around 0-minute area represent matches that have been input to Club Locker in mere seconds. This is most probably due to inserting the matches into Club Locker retroactively post-match. It is unreasonable to think that the matches actually took less than a few minutes.

        Let's look at the same data from a slightly different perspective:
        """
    )

    fig, ax = plt.subplots()
    fig.tight_layout()
    sn.histplot(
        ax=ax,
        data=matches_df.rename(
            columns={
                "NumberOfGames": "Games",
            }
        ),
        x="MatchDuration",
        hue="Games",
        binwidth=1,
        multiple="stack",
        legend=True,
        palette=custom_palette_3,
    )
    ax.set_xlim(-5, 90)
    ax.set_xlabel("Match duration (minutes)")
    match_container.pyplot(fig)
    match_container.markdown(
        caption_text("Figure 10", "Distribution of match durations."),
        unsafe_allow_html=True,
    )

    match_container.markdown(
        f"""
        It is interesting to note that so many of the 3-game matches are less than 20 minutes long. You could roughly say, that 4-game matches are around 25 minutes long and 5-game matches are around 35 minutes long. Some of the longest 5-gamers are around 80 minutes in length.
        """
    )

    ending_container = st.container()
    ending_container.markdown(
        f"""
        # 7. The End
        Congratulations - you have reached the end of the study! In this study, we took a brief look on the Club Locker competition data and perhaps learned something new. I am not going to iterate the findings in any more depth in this section.

        If you feel inspired, or if you have ideas about further research, feel free to contact me. I hope you found this study amusing.

        Thank you for reading.

        Best regards,
        *Ilmari Vikström*

        **PS. Do not forget to open the sidebar and go take a look at the "Player vs. Player Analyzer". There you are able to see how well you do against your opponents.**
        """
    )


def player_vs_player(st, **state):
    custom_css(background_path="res/neon_court4.png")
    _, header_image_container, _ = st.columns([1, 4, 1])
    header_image_container.image(
        "res/court4.png", caption="Imagery: ASB TPoint Squash Courts"
    )
    header_text_container = st.container()
    header_text_container.title(
        """
        Player vs. Player Analyzer
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
    loading_container = st.container()
    loading_container.markdown(
        """
        This tool allows you to pick and compare two individual players with each other. Please go ahead and pick the players from the dropdown menus.
        """
    )

    # TODO: Do data loading somewhere else? Maybe a landing page.
    tournaments_df = load_tournaments(skip=config.data["skip_fetch"])
    matches_df = load_matches(
        skip=config.data["skip_fetch"], tournaments_df=tournaments_df
    )
    rankings_df = load_rankings(skip=config.data["skip_fetch"])

    player_1_selection_container, player_2_selection_container = st.columns(2)
    unique_player_names = np.sort(
        pd.unique(matches_df[["vPlayerName", "hPlayerName"]].values.ravel("K"))
    )
    unique_player_names = np.concatenate((["Select a player"], unique_player_names))

    active_players_df = (
        pd.concat(
            [
                matches_df.groupby(by=["LoserPlayer"])
                .count()
                .reset_index(names="Player"),
                matches_df.groupby(by=["WinnerPlayer"])
                .count()
                .reset_index(names="Player"),
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

    player_1_name = player_1_selection_container.selectbox(
        label="Player 1", options=unique_player_names, key="player_1_selection"
    )
    player_2_name = player_2_selection_container.selectbox(
        label="Player 2", options=unique_player_names, key="player_2_selection"
    )
    player_1_ok = False
    player_2_ok = False

    if player_1_name != "Select a player":
        if (
            len(
                rankings_df.loc[
                    (rankings_df["firstName"] == player_1_name.split(" ")[0])
                    & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                ].values.tolist()
            )
            > 0
        ):
            player_1_ok = True
        else:
            player_1_selection_container.error("Player not in rankings.")

    if player_2_name != "Select a player":
        if (
            len(
                rankings_df.loc[
                    (rankings_df["firstName"] == player_2_name.split(" ")[0])
                    & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                ].values.tolist()
            )
            > 0
        ):
            player_2_ok = True
        else:
            player_2_selection_container.error("Player not in rankings.")

    if player_1_name == player_2_name and (
        player_1_name != "Select a player" and player_2_name != "Select a player"
    ):
        error_container = st.container()
        error_container.error("Please select two different players.")
    elif player_1_ok and player_2_ok:
        if (player_1_name != "Select a player") and (
            player_2_name != "Select a player"
        ):
            data = {
                "metrics": [
                    "Age",
                    "Rating",
                    "Ranking",
                    "Matches",
                    "Wins",
                    "Losses",
                    "Win Percentage",
                ],
                player_1_name: [
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["age"].values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["rating"].values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["ranking"].values.tolist()[0],
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["TotalMatches"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["WinnerPlayer"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["LoserPlayer"].values.tolist()[0]
                    ),
                    round(
                        100
                        * int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_1_name
                            ]["WinnerPlayer"].values.tolist()[0]
                        )
                        / int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_1_name
                            ]["TotalMatches"].values.tolist()[0]
                        )
                    ),
                ],
                player_2_name: [
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["age"].values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["rating"].values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["ranking"].values.tolist()[0],
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["TotalMatches"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["WinnerPlayer"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["LoserPlayer"].values.tolist()[0]
                    ),
                    round(
                        100
                        * int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_2_name
                            ]["WinnerPlayer"].values.tolist()[0]
                        )
                        / int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_2_name
                            ]["TotalMatches"].values.tolist()[0]
                        )
                    ),
                ],
            }
            data = {
                "Name": [
                    player_1_name,
                    player_2_name,
                ],
                "Age": [
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["age"].values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["age"].values.tolist()[0],
                ],
                "Rating": [
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["rating"]
                    .fillna(0)
                    .values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["rating"]
                    .fillna(0)
                    .values.tolist()[0],
                ],
                "Ranking": [
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_1_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_1_name.split(" ")[1])
                    ]["ranking"]
                    .fillna(0)
                    .values.tolist()[0],
                    rankings_df.loc[
                        (rankings_df["firstName"] == player_2_name.split(" ")[0])
                        & (rankings_df["lastName"] == player_2_name.split(" ")[1])
                    ]["ranking"]
                    .fillna(0)
                    .values.tolist()[0],
                ],
                "Matches": [
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["TotalMatches"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["TotalMatches"].values.tolist()[0]
                    ),
                ],
                "Wins": [
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["WinnerPlayer"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["WinnerPlayer"].values.tolist()[0]
                    ),
                ],
                "Losses": [
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_1_name
                        ]["LoserPlayer"].values.tolist()[0]
                    ),
                    int(
                        active_players_df.loc[
                            active_players_df["Player"] == player_2_name
                        ]["LoserPlayer"].values.tolist()[0]
                    ),
                ],
                "Win Percentage": [
                    round(
                        100
                        * int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_1_name
                            ]["WinnerPlayer"].values.tolist()[0]
                        )
                        / int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_1_name
                            ]["TotalMatches"].values.tolist()[0]
                        )
                    ),
                    round(
                        100
                        * int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_2_name
                            ]["WinnerPlayer"].values.tolist()[0]
                        )
                        / int(
                            active_players_df.loc[
                                active_players_df["Player"] == player_2_name
                            ]["TotalMatches"].values.tolist()[0]
                        )
                    ),
                ],
            }
            comparison_container = st.container()
            dataframe = pd.DataFrame.from_dict(data)
            dataframe = dataframe.set_index("Name")
            dark_green = "#00ff0033"
            dark_red = "#ff000033"
            comparison_container.dataframe(
                (dataframe.style)
                .highlight_max(axis=0, subset=["Rating"], color=dark_green)
                .highlight_min(axis=0, subset=["Rating"], color=dark_red)
                .highlight_max(axis=0, subset=["Ranking"], color=dark_red)
                .highlight_min(axis=0, subset=["Ranking"], color=dark_green)
                .highlight_max(axis=0, subset=["Matches"], color=dark_green)
                .highlight_min(axis=0, subset=["Matches"], color=dark_red)
                .highlight_max(axis=0, subset=["Wins"], color=dark_green)
                .highlight_min(axis=0, subset=["Wins"], color=dark_red)
                .highlight_max(axis=0, subset=["Losses"], color=dark_red)
                .highlight_min(axis=0, subset=["Losses"], color=dark_green)
                .highlight_max(axis=0, subset=["Win Percentage"], color=dark_green)
                .highlight_min(axis=0, subset=["Win Percentage"], color=dark_red),
                use_container_width=True,
            )
            comparison_container.markdown("---")


app = MultiPage(navbar_style="SelectBox", hide_navigation=True)
app.st = st

app.add_app("Tournament Data Study", data_analysis)
app.add_app("Player vs. Player Analyzer", player_vs_player)

app.run()
