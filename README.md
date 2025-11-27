# European Soccer Analytics Platform

A comprehensive soccer analytics platform built with MongoDB, Flask, and Machine Learning for analyzing 25,000+ European soccer matches from 2008-2016.

**Course:** DS5760 NoSQL for Modern Data Science Applications  
**Student:** Roshan Sivakumar  
**GitHub:** [rroshann/soccer-analytics-mongodb](https://github.com/rroshann/soccer-analytics-mongodb)

---

## 🎯 Project Overview

This project demonstrates mastery of NoSQL databases by building a full-stack soccer analytics application with:
- **MongoDB** for flexible data storage and complex queries
- **Flask** web interface with 7 interactive queries
- **Machine Learning** model for match outcome prediction (50% accuracy)
- **25,979 matches** from 11 European leagues
- **11,060 players** with FIFA attributes over time
- **299 teams** with tactical attributes

---

## 🏆 Key Features

### 1. Interactive Query System
- **Query 1:** Team Performance by Season (league standings)
- **Query 2:** Home vs Away Performance Analysis
- **Query 3:** Head-to-Head Historical Records
- **Query 4:** Player Appearance Frequency
- **Query 5:** Team Form Analysis (recent momentum)
- **Query 6:** High-Scoring vs Low-Scoring Teams
- **Query 7:** Team Attributes Correlation with Success

### 2. Machine Learning Prediction
- Gradient Boosting model trained on 25,000+ matches
- Predicts match outcomes (Home Win / Draw / Away Win)
- 50% accuracy (typical for soccer prediction)
- Key finding: Recent form is the most important predictor (22% feature importance)

### 3. Web Interface
- Clean, responsive design
- Real-time predictions with probability distributions
- Interactive data exploration
- Dynamic visualizations

---

## 📊 Dataset

**Source:** [Kaggle - European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer)

**Contents:**
- 25,979 matches (2008-2016)
- 11 European leagues (Premier League, La Liga, Bundesliga, Serie A, etc.)
- Player and team attributes from FIFA ratings
- Match events, lineups, betting odds

---

## 🛠️ Technologies Used

- **Database:** MongoDB 7.x (Docker)
- **Backend:** Python 3.8+, Flask
- **ML:** Scikit-learn (Gradient Boosting, Random Forest)
- **Data Processing:** Pandas, NumPy
- **Frontend:** HTML, CSS, JavaScript (Vanilla)

---

## 🚀 Setup Instructions

### Prerequisites
```bash
- Python 3.8+
- Docker Desktop
- MongoDB (via Docker)
```

### 1. Clone Repository
```bash
git clone https://github.com/rroshann/soccer-analytics-mongodb.git
cd soccer-analytics-mongodb
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download Dataset
1. Go to [Kaggle European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer)
2. Download `database.sqlite` (299MB)
3. Place it in the project root directory

### 4. Start MongoDB (Docker)
```bash
docker-compose up -d
```

Verify MongoDB is running:
```bash
docker ps
```

### 5. Convert Data to MongoDB
```bash
python scripts/convert_sqlite_to_mongo.py
```

This will:
- Create 4 collections: matches, players, teams, leagues
- Import 25,979 matches
- Create indexes for performance
- Takes ~2-3 minutes

### 6. Train ML Model
```bash
python scripts/train_ml_model_improved.py
```

This will:
- Train Gradient Boosting model
- Test 3 different algorithms
- Save best model to `data/model/rf_model.pkl`
- Takes ~1-2 minutes

### 7. Run Flask Application
```bash
python app/app.py
```

Open browser: `http://localhost:5001`

---

## 📁 Project Structure

```
soccer-analytics-mongodb/
├── app/
│   ├── app.py                    # Flask application
│   └── templates/
│       ├── base.html             # Base template
│       ├── index.html            # Home page
│       ├── predict.html          # ML prediction interface
│       ├── queries.html          # Query documentation
│       ├── query1.html           # Team Performance
│       ├── query2.html           # Home vs Away
│       ├── query3.html           # Head-to-Head
│       ├── query4.html           # Player Appearances
│       ├── query5.html           # Team Form
│       ├── query6.html           # Scoring Analysis
│       └── query7.html           # Attributes Correlation
├── scripts/
│   ├── convert_sqlite_to_mongo.py   # Data conversion
│   ├── train_ml_model_improved.py   # ML training
│   └── queries/
│       ├── query1_team_performance.py
│       ├── query2_home_away.py
│       ├── query3_head_to_head.py
│       ├── query4_player_appearances.py
│       ├── query5_team_form.py
│       ├── query6_scoring_analysis.py
│       └── query7_attributes_correlation.py
├── data/
│   └── model/
│       └── rf_model.pkl          # Trained ML model
├── docker-compose.yml            # MongoDB configuration
├── requirements.txt              # Python dependencies
├── .gitignore
└── README.md
```

---

## 🎮 Usage Examples

### Running Individual Queries (Command Line)
```bash
# Query 1: Team Performance
python scripts/queries/query1_team_performance.py

# Query 3: Head-to-Head (Man United vs Liverpool)
python scripts/queries/query3_head_to_head.py

# Query 5: Team Form Analysis
python scripts/queries/query5_team_form.py
```

### Using Web Interface
1. Start Flask app: `python app/app.py`
2. Navigate to `http://localhost:5001`
3. **Home Page:** View database statistics
4. **Match Predictor:** Select two teams, get ML prediction with probabilities
5. **Explore Data:** Click on any query to run it interactively

---

## 📈 Query Demonstrations

### Query 1: Team Performance by Season
**Example Result:** Leicester City won 2015/2016 with 81 points (23W-12D-3L)

**MongoDB Features:** Aggregation, grouping, sorting

**What it does:** Calculates complete league standings with wins, draws, losses, goals for/against, goal difference, and points.

---

### Query 2: Home vs Away Performance
**Example Result:** Manchester United had +26.3% home advantage in 2015/2016

**MongoDB Features:** Conditional aggregation, percentage calculations

**What it does:** Compares each team's win rate at home vs away to identify home field advantage patterns.

---

### Query 3: Head-to-Head Records
**Example Result:** Man United vs Liverpool - 16 matches, 56.2% vs 37.5% win rate

**MongoDB Features:** $or operator, date sorting, match filtering

**What it does:** Shows complete match history between any two teams with win/loss/draw statistics and goals summary.

---

### Query 4: Player Appearance Frequency
**Example Result:** 8 players played all 38 matches in 2015/2016 (Simon Francis, Kasper Schmeichel, etc.)

**MongoDB Features:** Array queries, nested document access

**What it does:** Identifies the most consistent players by counting appearances, showing team loyalty and fitness.

---

### Query 5: Team Form Analysis
**Example Result:** Leicester's last 10 games: WWWWWDWDWD (7W-3D-0L, 24 points)

**MongoDB Features:** Time-series analysis, date-based sorting

**What it does:** Analyzes recent performance to identify momentum, winning streaks, and current team form.

---

### Query 6: High-Scoring vs Low-Scoring Teams
**Example Result:** Man City best attack (1.87 goals/game), Man United best defense (0.92 conceded/game)

**MongoDB Features:** Aggregation, average calculations, multi-sort

**What it does:** Classifies teams as offensive or defensive based on goals scored and conceded per match.

---

### Query 7: Team Attributes Correlation with Success
**Example Result:** Stronger team wins 39.5% of the time - attributes DO matter!

**MongoDB Features:** Complex joins, correlation analysis, bucketing

**What it does:** Analyzes if FIFA team ratings predict match outcomes. Validates using attributes as ML model features.

**Key Insight:** When rating difference is large (+10 to +15), stronger team wins 54% of the time. This proves correlation exists!

---

## 🤖 Machine Learning Model

### Model Details
- **Algorithm:** Gradient Boosting Classifier (best of 3 tested)
- **Accuracy:** 49.96% (~50%)
- **Training Data:** 25,629 matches
- **Features:** 15 total (team ratings, recent form, attack/defense stats, home advantage)

### Performance Breakdown
| Outcome | Precision | Recall | F1-Score |
|---------|-----------|--------|----------|
| Away Win | 0.475 | 36.9% | 0.415 |
| Draw | 0.226 | 2.8% | 0.050 |
| Home Win | 0.519 | 84.2% | 0.642 |

**Overall Accuracy:** 50%

### Why 50% is Actually Good
Soccer is inherently unpredictable:
- Draws happen ~25% of the time
- Upsets are common (weaker teams win 32% of the time)
- Even professional betting models struggle to exceed 55% accuracy
- Our model excels at predicting home wins (84% recall)

### Most Important Features
1. **form_diff** (22.0%) - Recent form difference between teams
2. **defense_diff** (7.9%) - Defensive rating difference
3. **away_attack** (7.2%) - Away team's attacking strength
4. **home_form** (6.7%) - Home team's recent 5-game form
5. **away_build_up** (6.4%) - Away team's build-up play speed

**Key Finding:** Recent form matters MORE than static FIFA ratings! This validates incorporating temporal data.

---

## 🔍 MongoDB Design Decisions

### Why MongoDB?
1. **Flexible Schema:** Match events vary (different numbers of goals, cards, substitutions per match)
2. **Nested Documents:** Perfect for embedding player lineups and team information directly in match documents
3. **Array Support:** Naturally handles multiple goal scorers, assists, and cards per match
4. **Aggregation Pipeline:** Ideal for calculating league tables, player statistics, and team performance metrics
5. **Scalability:** Efficiently handles 25k+ matches and 11k+ players with proper indexing

### Collections Design

#### matches Collection (Denormalized)
```javascript
{
  _id: ObjectId("..."),
  date: ISODate("2015-08-08T00:00:00.000Z"),
  season: "2015/2016",
  league_name: "England Premier League",
  home_team: {
    api_id: 9825,
    name: "Manchester United",
    short_name: "MUN"
  },
  away_team: {
    api_id: 8650,
    name: "Tottenham Hotspur",
    short_name: "TOT"
  },
  home_team_goal: 1,
  away_team_goal: 0,
  home_lineup: [
    { player_api_id: 30572, player_name: "David de Gea", position: 1 },
    { player_api_id: 37412, player_name: "Chris Smalling", position: 2 },
    // ... more players
  ],
  away_lineup: [ /* ... */ ]
}
```

**Why denormalized?**
- Reduces joins for common queries
- Faster reads (most queries need team names)
- Trade-off: Slightly slower writes, but we prioritize read performance

#### players Collection (With Temporal Data)
```javascript
{
  _id: ObjectId("..."),
  player_api_id: 30572,
  player_name: "David de Gea",
  birthday: "1990-11-07",
  height: 192,
  weight: 76,
  attributes_history: [
    {
      date: ISODate("2015-08-01T00:00:00.000Z"),
      overall_rating: 83,
      potential: 89,
      preferred_foot: "right",
      // ... 35+ more attributes
    },
    // ... historical ratings across seasons
  ]
}
```

### Indexing Strategy
```javascript
// Match indexes for performance
db.matches.createIndex({ "date": 1 })
db.matches.createIndex({ "league_name": 1 })
db.matches.createIndex({ "season": 1 })
db.matches.createIndex({ "home_team.name": 1 })
db.matches.createIndex({ "away_team.name": 1 })

// Player indexes
db.players.createIndex({ "player_name": 1 })
db.players.createIndex({ "player_api_id": 1 })

// Team indexes
db.teams.createIndex({ "team_long_name": 1 })
db.teams.createIndex({ "team_api_id": 1 })
```

---

## 🎓 Learning Outcomes

This project demonstrates:

### NoSQL Database Design
- Denormalization strategies for read-heavy workloads
- Embedding vs referencing trade-offs
- Index design for query optimization
- Handling temporal data in documents

### MongoDB Query Techniques
- Complex aggregation pipelines
- Array operations and nested document queries
- Date-based filtering and sorting
- $or operator for multiple match conditions
- Grouping and statistical calculations

### Machine Learning Integration
- Feature engineering from database queries
- Training models on real-world data
- Model evaluation and interpretation
- Handling imbalanced classes (draws are rare)
- Understanding model limitations

### Full-Stack Development
- RESTful API design with Flask
- AJAX for dynamic content loading
- Responsive web design
- Data visualization in browser
- User experience design

### Real-World Data Challenges
- Missing data handling
- Data quality assessment
- Performance optimization
- Scalability considerations

---

## 📊 Project Metrics

- **Total Lines of Code:** ~3,000+
- **Development Time:** ~20 hours
- **Database Size:** 25,979 matches, 11,060 players, 299 teams
- **Query Count:** 7 complex queries, each with 3+ MongoDB operations
- **ML Model Size:** 15 features, 100 estimators
- **Web Routes:** 17 routes (7 pages + 7 APIs + 3 static)

---

## 🔧 Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
docker ps

# Restart MongoDB
docker-compose restart

# Check logs
docker logs github-mongodb-1
```

### Port 5000 Already in Use
Solution: Flask is configured to use port 5001 to avoid conflicts with macOS AirPlay Receiver.

### Model File Not Found
```bash
# Re-train the model
python scripts/train_ml_model_improved.py

# Verify file exists
ls -la data/model/
```

### Slow Queries
- Ensure indexes are created (happens automatically during data conversion)
- Check MongoDB logs: `docker logs github-mongodb-1`
- Use `.explain()` in MongoDB shell to analyze query performance

---

## 🚨 Known Limitations

### Dataset Limitations
1. **Individual Goal Scorers Not Tracked:** Dataset doesn't specify which player scored which goal
2. **Match Events as XML:** Goal times, cards stored as XML strings (not parsed in this version)
3. **Incomplete Lineups:** Some early matches missing player lineup data
4. **Historical Data Only:** Dataset ends in 2016

### Model Limitations
1. **Cannot Predict Draws Well:** Only 2.8% recall for draws (they're genuinely unpredictable)
2. **No Live Updates:** Model trained on historical data, doesn't update with new matches
3. **Simplified Features:** Doesn't account for injuries, suspensions, weather, referee bias
4. **Form Calculation Assumption:** Uses last 5 games, may not reflect longer-term trends

### Application Limitations
1. **No User Authentication:** Public access to all features
2. **No Caching:** Each query hits database directly
3. **Limited Error Handling:** Some edge cases may cause errors
4. **No Data Validation:** Assumes clean inputs from users

---

## 🔮 Future Enhancements

### Potential Improvements
1. **Real-Time Data:** Integrate with live match APIs for current season data
2. **Advanced Visualizations:** Add charts and graphs using D3.js or Chart.js
3. **User Accounts:** Save favorite teams, custom dashboards
4. **More ML Models:** Try neural networks, ensemble methods
5. **Player-Level Predictions:** Predict individual player performance
6. **Betting Odds Analysis:** Compare predictions to actual betting lines
7. **Mobile App:** React Native app for iOS/Android
8. **API Documentation:** Swagger/OpenAPI specs for public API

### Technical Improvements
1. **Caching Layer:** Redis for frequently accessed queries
2. **Background Jobs:** Celery for model training, data updates
3. **Database Replication:** MongoDB replica set for high availability
4. **Containerization:** Docker Compose for entire stack
5. **CI/CD Pipeline:** GitHub Actions for automated testing
6. **Performance Monitoring:** Application performance monitoring (APM)

---

## 📚 References

### Dataset
- [Kaggle - European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer)

### Technologies
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

### Research
- This project was inspired by real-world sports analytics and betting systems
- Soccer outcome prediction is a well-studied problem in machine learning
- Home field advantage is a documented phenomenon across all sports

---

## 📝 Submission Checklist

For DS5760 Final Project:

- [x] Proposal (1-2 pages) submitted
- [x] MongoDB database designed and implemented
- [x] Dataset curated (25,979 matches)
- [x] 7 distinct queries implemented (Python + Web)
- [x] Extension component 1: Flask Web UI
- [x] Extension component 2: Machine Learning model
- [x] GitHub repository with code
- [x] README documentation
- [x] Query screenshots captured
- [ ] Final presentation prepared
- [ ] Demo rehearsed

---

## 🎬 Demo Script

### Quick Demo (5 minutes)
1. **Intro (30 sec):** "Built soccer analytics platform with MongoDB, analyzed 25k matches"
2. **Database (1 min):** Show MongoDB collections, explain denormalization
3. **Query Demo (2 min):** 
   - Query 1: Leicester City championship season
   - Query 5: Team form analysis showing momentum
4. **ML Prediction (1 min):** Live prediction of Man United vs Liverpool
5. **Conclusion (30 sec):** "Demonstrates NoSQL design, complex queries, ML integration"

### Full Demo (10 minutes)
- Add Query 3 (Head-to-Head) and Query 7 (Attributes Correlation)
- Show code snippets for one query
- Discuss model performance and why 50% is realistic
- Take questions

---

## 👨‍💻 Author

**Roshan Sivakumar**  
- GitHub: [@rroshann](https://github.com/rroshann)
- Project: [soccer-analytics-mongodb](https://github.com/rroshann/soccer-analytics-mongodb)

---

## 📄 License

This project was created for academic purposes as part of DS5760 coursework.

The dataset is from Kaggle and is subject to its own license terms.

---

## 🙏 Acknowledgments

- **Professor:** Professor Dana Zhang for project guidance
- **Kaggle:** For providing the European Soccer Database
- **MongoDB:** For excellent NoSQL database technology
- **Scikit-learn:** For robust machine learning tools
- **Flask:** For lightweight web framework

---

**Last Updated:** November 26, 2024

**Project Status:** ✅ Complete and Deployed
