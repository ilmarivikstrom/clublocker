# Clublocker

- [ ] Historical ranking
  - [ ] Fetch Ranking periods: https://api.ussquash.com/resources/ranking-groups/9/periods
  - [ ] Fetch Divions for ranking periods: https://api.ussquash.com/resources/ranking-groups/9/divisions?rankingPeriod=2022-11-14
  - [ ] Fetch Rankings for a period: https://api.ussquash.com/resources/rankings/9/2022-11-14?divisions=1&pageNumber=1&rowsPerPage=1000
  - [ ] Based on these queries, construct a time series of rating/points & ranking for each player.
- [ ] Player data
  - [ ] Show player activity related to the ranking.
  ```
  active_players_df["FirstName"] = active_players_df["Player"].str.split(" ").str[0]
  active_players_df["LastName"] = active_players_df["Player"].str.split(" ").str[1]
  rankings_and_activity_df = rankings_df.merge(active_players_df, left_on=["firstName", "lastName"], right_on=["FirstName", "LastName"])[["ranking", "Player", "TotalMatches", "division"]]
  rankings_and_activity_df["TotalMatches"] = rankings_and_activity_df["TotalMatches"].astype(int)

  fig, ax = plt.subplots()
  sn.barplot(data=rankings_and_activity_df.loc[rankings_and_activity_df["division"] == "All Men"].rolling(20).mean(), x="ranking", y="TotalMatches")
  player_activity_container.pyplot(fig)
  fig, ax = plt.subplots()
  sn.histplot(
      ax=ax,
      data=rankings_and_activity_df.loc[rankings_and_activity_df["division"] == "All Men"],
      x="ranking",
      y="TotalMatches",
      binwidth=10,
      multiple="stack",
      legend=True,
      palette=custom_palette_cmap,
  )
  player_activity_container.pyplot(fig)
```
- [ ] Tournaments
  - [ ] Calculate and visualize the influx of new players never seen in previous tournaments.
- [ ] Match data
  - [ ] Longest matches: `matches_df.sort_values(by=["Rallies"], ascending=False).head(20)[["MatchDate", "Title", "Rallies", "Score_Short", "WinnerPlayer", "LoserPlayer", "Year", "Month"]]`
- [ ] 