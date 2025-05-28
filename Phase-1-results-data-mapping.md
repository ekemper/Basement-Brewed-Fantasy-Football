# Heat map sections:
## Games: 
**data points example:**
```
 {
 "matchup": "49ers at Bills",
      "game_data": {
        "game_id": 15,
        "away_team": "49ers",
        "home_team": "Bills",
        "over_under": 44.5,
        "away_spread": 6.5,
        "home_spread": -6.5,
        "away_implied": 19,
        "home_implied": 25.5
      }
 }
```
![alt text](<Screenshot 2025-05-27 at 7.50.43 PM.png>)

**data source:**
```
https://sportsbook.draftkings.com/leagues/football/nfl
```

The implied points for each team are calculated with the following formula:
'''
Implied Points = ( over under / 2 ) - ( spread / 2 )
'''






# Current Challenges for data acquisition:

Pro Football Reference has strict rate limiting on scraping
* I will have to do some experimentation on how to not get IP blocked