# European Soccer Analytics Platform

## Project Overview

- Soccer analytics platform using MongoDB, Flask, and Machine Learning
- 25,979 matches, 11,060 players, 299 teams from 11 European leagues (2008-2016)
- Converted SQLite to MongoDB, built 7 analytical queries, added ML predictions

**Key Stats:**
- 25,979 matches from 11 European leagues
- 11,060 players with FIFA attributes
- 299 teams with tactical attributes
- 7 complex MongoDB queries
- Machine Learning model for match predictions

---

## Database Design & Justification

### Why MongoDB?

- **Flexible Schema:** Match events vary (different goals, cards per match) - MongoDB handles this naturally
- **Nested Documents:** Embed player lineups and team info directly in match documents - no joins needed
- **Array Support:** Handle multiple players, goals, events without complex normalization
- **Aggregation Pipeline:** Perfect for calculating league tables and statistics

### Design Decisions

- **Denormalization:** Embedded team/player info in matches for faster queries (read-heavy workload)
- **4 Collections:** matches, players, teams, leagues
- **Indexing:** Strategic indexes on date, league, season, team names for performance

---

## Data Curation

- **Source:** Kaggle European Soccer Database (SQLite, 299MB)
- **Conversion:** Custom Python script converts relational data to MongoDB documents
- **Result:** 
  - 25,979 matches successfully imported
  - All team/player data embedded in match documents
  - Indexes created automatically for query optimization

---

## Query Implementation

**7 Distinct Queries:**

1. **Team Performance by Season** - League standings with wins, draws, losses, points
2. **Home vs Away Performance** - Home field advantage analysis
3. **Head-to-Head Records** - Complete match history between two teams
4. **Player Appearance Frequency** - Most consistent players
5. **Team Form Analysis** - Recent momentum (last N games)
6. **Scoring Analysis** - Offensive vs defensive teams
7. **Attributes Correlation** - FIFA ratings vs match outcomes

**Each query demonstrates different MongoDB operations:**
- Aggregation and grouping
- Array queries
- $or operator
- Time-series analysis
- Correlation analysis

---

## Extension Components

### Machine Learning Model

- **Purpose:** Predict match outcomes (Home Win / Draw / Away Win)
- **Algorithm:** Gradient Boosting Classifier
- **Performance:** 50% accuracy (typical for soccer prediction)
- **Key Finding:** Recent form (22% importance) matters more than static FIFA ratings
- **Features:** 15 features including team ratings, recent form, attack/defense stats

### Flask Web Interface

- **Interactive web application** for all queries and predictions
- **17 routes:** 7 query pages + 7 API endpoints + 3 static pages
- **Real-time predictions** with ML model integration
- **RESTful APIs** for seamless data loading

---

## Live Demo

I'm going to demonstrate the working application now.

### Home Dashboard

- Show database statistics: 25k matches, 11k players, 299 teams
- Navigate to queries page

### Query 1 - Team Performance

- Select: "England Premier League" → "2015/2016"
- Show results: Leicester City won with 81 points
- This calculates complete league standings using MongoDB aggregation

**Query Flow:**
1. User selects league and season → JavaScript sends POST request to `/api/query1`
2. Flask receives request → Converts to MongoDB query: `db.matches.find({'league_name': league, 'season': season})`
3. MongoDB executes query → Returns all match documents for that league/season
4. Python processes results → Loops through matches, calculates wins/draws/losses, goals, points for each team
5. Python sorts standings → By points, then goal difference
6. Flask returns JSON → Standings table with team statistics
7. JavaScript displays results → Formatted table on web page

### Query 2 - Home vs Away Performance

- Select: "England Premier League" → "2015/2016"
- Show results comparing home win rates vs away win rates for each team
- Identifies teams with strongest home field advantage
- Uses conditional aggregation to separate home and away statistics

### Query 3 - Head-to-Head

- Select: "Manchester United" vs "Liverpool"
- Show match history and statistics
- Uses $or operator to find matches where either team is home or away

### Query 4 - Player Appearance Frequency

- Select: "England Premier League" → "2015/2016"
- Show top players by appearance count
- Demonstrates array queries on nested lineup data
- Identifies most consistent players who played all matches

### Query 5 - Team Form

- Select team, league, and season
- Show recent form analysis with form string (WWWDL) and points
- Analyzes last N games to show current momentum
- Uses time-series analysis with date-based sorting

### Query 6 - Scoring Analysis

- Select: "England Premier League" → "2015/2016"
- Show teams ranked by goals scored per game (best attack)
- Show teams ranked by goals conceded per game (best defense)
- Classifies teams as offensive or defensive based on scoring patterns

### Query 7 - Attributes Correlation

- Select: "England Premier League" → "2015/2016"
- Show correlation between FIFA team ratings and match outcomes
- Demonstrates bucketing by rating differences
- Shows how often stronger teams win based on attribute differences

### ML Prediction

- Go to "Predict Match" page
- Select two teams (e.g., Man United vs Liverpool)
- Show prediction with probabilities
- ML model uses 15 features including team ratings and recent form
- 50% accuracy, with 84% recall for home wins

---

## Known Limitations

### Dataset Limitations
- Individual goal scorers not tracked in dataset
- Match events stored as XML strings (not parsed)
- Some early matches missing player lineup data
- Historical data only (ends in 2016)

### Model Limitations
- Cannot predict draws well (only 2.8% recall)
- No live updates - model trained on historical data
- Simplified features - doesn't account for injuries, weather, referee bias
- Form calculation uses last 5 games assumption

### Application Limitations
- No user authentication
- No caching - each query hits database directly
- Limited error handling for edge cases
- No data validation on user inputs

---

## Future Enhancements

### Potential Improvements
- Real-time data integration with live match APIs
- User accounts with favorite teams and custom dashboards
- Player-level predictions
- Betting odds analysis
- Mobile app development
---

## Conclusion

**Key Takeaways:**

- Successfully designed MongoDB database with denormalized structure
- Implemented 7 complex queries demonstrating various MongoDB operations
- Built Machine Learning model for match outcome prediction
- Created full-stack web application with Flask
- Demonstrated practical NoSQL database design and implementation
