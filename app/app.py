"""
Flask Web Application for Soccer Analytics
"""

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pickle
import sys
import os

# Add parent directory to path to import query functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['soccer_analytics']

# Load ML model
model_path = 'data/model/rf_model.pkl'
with open(model_path, 'rb') as f:
    model_data = pickle.load(f)
    ml_model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']

@app.route('/')
def home():
    """Home page with dashboard"""
    # Get summary stats
    stats = {
        'total_matches': db.matches.count_documents({}),
        'total_players': db.players.count_documents({}),
        'total_teams': db.teams.count_documents({}),
        'total_leagues': db.leagues.count_documents({})
    }
    
    return render_template('index.html', stats=stats)

@app.route('/predict')
def predict_page():
    """Match prediction page"""
    # Get unique teams
    teams = sorted(db.teams.distinct('team_long_name'))
    
    return render_template('predict.html', teams=teams)

@app.route('/api/predict', methods=['POST'])
def predict_match():
    """API endpoint for match predictions"""
    data = request.get_json()
    
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    
    if not home_team or not away_team:
        return jsonify({'error': 'Both teams required'}), 400
    
    try:
        # Get team attributes
        home_team_data = db.teams.find_one({'team_long_name': home_team})
        away_team_data = db.teams.find_one({'team_long_name': away_team})
        
        if not home_team_data or not away_team_data:
            return jsonify({'error': 'Team not found'}), 404
        
        # Get latest attributes
        home_attrs = home_team_data['attributes_history'][-1] if home_team_data.get('attributes_history') else {}
        away_attrs = away_team_data['attributes_history'][-1] if away_team_data.get('attributes_history') else {}
        
        # Calculate features
        home_rating = (home_attrs.get('buildUpPlaySpeed', 50) + 
                      home_attrs.get('defencePressure', 50) + 
                      home_attrs.get('chanceCreationShooting', 50)) / 3
        
        away_rating = (away_attrs.get('buildUpPlaySpeed', 50) + 
                      away_attrs.get('defencePressure', 50) + 
                      away_attrs.get('chanceCreationShooting', 50)) / 3
        
        # Build feature vector
        feature_dict = {
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_diff': home_rating - away_rating,
            'home_build_up': home_attrs.get('buildUpPlaySpeed', 50),
            'away_build_up': away_attrs.get('buildUpPlaySpeed', 50),
            'home_defense': home_attrs.get('defencePressure', 50),
            'away_defense': away_attrs.get('defencePressure', 50),
            'home_attack': home_attrs.get('chanceCreationShooting', 50),
            'away_attack': away_attrs.get('chanceCreationShooting', 50),
            'attack_diff': home_attrs.get('chanceCreationShooting', 50) - away_attrs.get('chanceCreationShooting', 50),
            'defense_diff': home_attrs.get('defencePressure', 50) - away_attrs.get('defencePressure', 50),
            'home_advantage': 1
        }
        
        # Add form features if model has them
        if 'home_form' in features:
            feature_dict['home_form'] = 0.5
            feature_dict['away_form'] = 0.5
            feature_dict['form_diff'] = 0.0
        
        # Create feature array in correct order
        X = [[feature_dict[f] for f in features]]
        
        # Scale and predict
        X_scaled = scaler.transform(X)
        probabilities = ml_model.predict_proba(X_scaled)[0]
        
        result = {
            'home_team': home_team,
            'away_team': away_team,
            'probabilities': {
                'away_win': round(probabilities[0] * 100, 2),
                'draw': round(probabilities[1] * 100, 2),
                'home_win': round(probabilities[2] * 100, 2)
            },
            'prediction': ['Away Win', 'Draw', 'Home Win'][probabilities.argmax()],
            'confidence': round(probabilities.max() * 100, 2),
            'team_attributes': {
                'home': {
                    'rating': round(home_rating, 1),
                    'attack': home_attrs.get('chanceCreationShooting', 50),
                    'defense': home_attrs.get('defencePressure', 50)
                },
                'away': {
                    'rating': round(away_rating, 1),
                    'attack': away_attrs.get('chanceCreationShooting', 50),
                    'defense': away_attrs.get('defencePressure', 50)
                }
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/queries')
def queries_page():
    """Queries demonstration page"""
    # Get available leagues and seasons
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    teams = sorted(db.teams.distinct('team_long_name'))
    
    return render_template('queries.html', leagues=leagues, seasons=seasons, teams=teams)


@app.route('/query1')
def query1_page():
    """Query 1: Team Performance"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    return render_template('query1.html', leagues=leagues, seasons=seasons)

@app.route('/api/query1', methods=['POST'])
def api_query1():
    """API endpoint for Query 1"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    
    try:
        matches = db.matches.find({
            'league_name': league,
            'season': season
        })
        
        teams = {}
        
        for match in matches:
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Initialize teams
            if home_team not in teams:
                teams[home_team] = {
                    'team': home_team,
                    'played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'goals_for': 0,
                    'goals_against': 0,
                    'goal_diff': 0,
                    'points': 0
                }
            
            if away_team not in teams:
                teams[away_team] = {
                    'team': away_team,
                    'played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'goals_for': 0,
                    'goals_against': 0,
                    'goal_diff': 0,
                    'points': 0
                }
            
            # Update stats
            teams[home_team]['played'] += 1
            teams[home_team]['goals_for'] += home_goals
            teams[home_team]['goals_against'] += away_goals
            
            teams[away_team]['played'] += 1
            teams[away_team]['goals_for'] += away_goals
            teams[away_team]['goals_against'] += home_goals
            
            # Results
            if home_goals > away_goals:
                teams[home_team]['wins'] += 1
                teams[home_team]['points'] += 3
                teams[away_team]['losses'] += 1
            elif home_goals < away_goals:
                teams[away_team]['wins'] += 1
                teams[away_team]['points'] += 3
                teams[home_team]['losses'] += 1
            else:
                teams[home_team]['draws'] += 1
                teams[home_team]['points'] += 1
                teams[away_team]['draws'] += 1
                teams[away_team]['points'] += 1
        
        # Calculate goal difference
        for team in teams.values():
            team['goal_diff'] = team['goals_for'] - team['goals_against']
        
        # Sort standings
        standings = sorted(teams.values(), 
                          key=lambda x: (x['points'], x['goal_diff']), 
                          reverse=True)
        
        # Get summary stats
        top_scorer = max(teams.values(), key=lambda x: x['goals_for'])
        best_defense = min(teams.values(), key=lambda x: x['goals_against'])
        
        return jsonify({
            'standings': standings,
            'top_scorer': top_scorer,
            'best_defense': best_defense
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
@app.route('/query2')
def query2_page():
    """Query 2: Home vs Away Performance"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    return render_template('query2.html', leagues=leagues, seasons=seasons)

@app.route('/api/query2', methods=['POST'])
def api_query2():
    """API endpoint for Query 2"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    
    try:
        matches = db.matches.find({
            'league_name': league,
            'season': season
        })
        
        teams = {}
        
        for match in matches:
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Initialize teams
            if home_team not in teams:
                teams[home_team] = {
                    'team': home_team,
                    'home_played': 0,
                    'home_wins': 0,
                    'home_draws': 0,
                    'home_losses': 0,
                    'home_points': 0,
                    'away_played': 0,
                    'away_wins': 0,
                    'away_draws': 0,
                    'away_losses': 0,
                    'away_points': 0
                }
            
            if away_team not in teams:
                teams[away_team] = {
                    'team': away_team,
                    'home_played': 0,
                    'home_wins': 0,
                    'home_draws': 0,
                    'home_losses': 0,
                    'home_points': 0,
                    'away_played': 0,
                    'away_wins': 0,
                    'away_draws': 0,
                    'away_losses': 0,
                    'away_points': 0
                }
            
            # Update home team (playing at home)
            teams[home_team]['home_played'] += 1
            if home_goals > away_goals:
                teams[home_team]['home_wins'] += 1
                teams[home_team]['home_points'] += 3
            elif home_goals == away_goals:
                teams[home_team]['home_draws'] += 1
                teams[home_team]['home_points'] += 1
            else:
                teams[home_team]['home_losses'] += 1
            
            # Update away team (playing away)
            teams[away_team]['away_played'] += 1
            if away_goals > home_goals:
                teams[away_team]['away_wins'] += 1
                teams[away_team]['away_points'] += 3
            elif away_goals == home_goals:
                teams[away_team]['away_draws'] += 1
                teams[away_team]['away_points'] += 1
            else:
                teams[away_team]['away_losses'] += 1
        
        # Calculate percentages
        results = []
        for team_data in teams.values():
            home_win_pct = round((team_data['home_wins'] / team_data['home_played'] * 100), 1) if team_data['home_played'] > 0 else 0
            away_win_pct = round((team_data['away_wins'] / team_data['away_played'] * 100), 1) if team_data['away_played'] > 0 else 0
            home_advantage = round(home_win_pct - away_win_pct, 1)
            
            results.append({
                'team': team_data['team'],
                'home_win_pct': home_win_pct,
                'away_win_pct': away_win_pct,
                'home_advantage': home_advantage,
                'home_points': team_data['home_points'],
                'away_points': team_data['away_points']
            })
        
        # Sort by home advantage
        results.sort(key=lambda x: x['home_advantage'], reverse=True)
        
        # Summary stats
        best_home = results[0]
        worst_home = results[-1]
        avg_advantage = round(sum(r['home_advantage'] for r in results) / len(results), 1)
        
        return jsonify({
            'results': results,
            'best_home': best_home,
            'worst_home': worst_home,
            'avg_advantage': avg_advantage
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/query3')
def query3_page():
    """Query 3: Head-to-Head Records"""
    teams = sorted(db.teams.distinct('team_long_name'))
    leagues = sorted(db.leagues.distinct('name'))
    return render_template('query3.html', teams=teams, leagues=leagues)

@app.route('/api/query3', methods=['POST'])
def api_query3():
    """API endpoint for Query 3"""
    data = request.get_json()
    team1 = data.get('team1')
    team2 = data.get('team2')
    league = data.get('league', '')
    
    try:
        # Build query
        query = {
            '$or': [
                {'home_team.name': team1, 'away_team.name': team2},
                {'home_team.name': team2, 'away_team.name': team1}
            ]
        }
        
        if league:
            query['league_name'] = league
        
        # Get matches
        matches = list(db.matches.find(query).sort('date', 1))
        
        if not matches:
            return jsonify({'error': f'No matches found between {team1} and {team2}'}), 404
        
        # Calculate stats
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals = 0
        team2_goals = 0
        
        match_details = []
        
        for match in matches:
            home = match['home_team']['name']
            away = match['away_team']['name']
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Determine result from team1's perspective
            if home == team1:
                team1_goals += home_goals
                team2_goals += away_goals
                if home_goals > away_goals:
                    team1_wins += 1
                    result = f"{team1} win"
                elif home_goals < away_goals:
                    team2_wins += 1
                    result = f"{team2} win"
                else:
                    draws += 1
                    result = "Draw"
            else:
                team1_goals += away_goals
                team2_goals += home_goals
                if away_goals > home_goals:
                    team1_wins += 1
                    result = f"{team1} win"
                elif away_goals < home_goals:
                    team2_wins += 1
                    result = f"{team2} win"
                else:
                    draws += 1
                    result = "Draw"
            
            match_details.append({
                'date': match['date'].strftime('%Y-%m-%d') if hasattr(match['date'], 'strftime') else str(match['date'])[:10],
                'season': match['season'],
                'home': home,
                'away': away,
                'score': f"{home_goals}-{away_goals}",
                'result': result
            })
        
        total_matches = len(matches)
        team1_win_pct = round((team1_wins / total_matches * 100), 1)
        team2_win_pct = round((team2_wins / total_matches * 100), 1)
        draw_pct = round((draws / total_matches * 100), 1)
        
        return jsonify({
            'team1': team1,
            'team2': team2,
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_goals': team1_goals,
            'team2_goals': team2_goals,
            'team1_win_pct': team1_win_pct,
            'team2_win_pct': team2_win_pct,
            'draw_pct': draw_pct,
            'matches': match_details
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/query4')
def query4_page():
    """Query 4: Player Appearance Frequency"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    return render_template('query4.html', leagues=leagues, seasons=seasons)

@app.route('/api/query4', methods=['POST'])
def api_query4():
    """API endpoint for Query 4"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    limit = data.get('limit', 15)
    
    try:
        matches = db.matches.find({
            'league_name': league,
            'season': season
        })
        
        player_stats = {}
        total_matches = 0
        
        for match in matches:
            total_matches += 1
            
            # Process home lineup
            for player in match.get('home_lineup', []):
                name = player.get('player_name')
                if name:
                    if name not in player_stats:
                        player_stats[name] = {
                            'player': name,
                            'appearances': 0,
                            'teams': set()
                        }
                    player_stats[name]['appearances'] += 1
                    player_stats[name]['teams'].add(match['home_team']['name'])
            
            # Process away lineup
            for player in match.get('away_lineup', []):
                name = player.get('player_name')
                if name:
                    if name not in player_stats:
                        player_stats[name] = {
                            'player': name,
                            'appearances': 0,
                            'teams': set()
                        }
                    player_stats[name]['appearances'] += 1
                    player_stats[name]['teams'].add(match['away_team']['name'])
        
        # Convert teams set to string
        for player in player_stats.values():
            player['teams'] = ', '.join(sorted(player['teams']))
        
        # Sort by appearances
        top_players = sorted(player_stats.values(), 
                            key=lambda x: x['appearances'], 
                            reverse=True)[:limit]
        
        # Count regulars (30+ appearances)
        regulars_count = sum(1 for p in player_stats.values() if p['appearances'] >= 30)
        
        # Total matches is half of what we counted (each match counted twice - home and away)
        actual_total_matches = total_matches // 2 if total_matches > 0 else 0
        # Actually, let's get accurate count
        actual_total_matches = db.matches.count_documents({
            'league_name': league,
            'season': season
        })
        
        return jsonify({
            'players': top_players,
            'total_matches': actual_total_matches,
            'regulars_count': regulars_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/query5')
def query5_page():
    """Query 5: Team Form Analysis"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    teams = sorted(db.teams.distinct('team_long_name'))
    return render_template('query5.html', leagues=leagues, seasons=seasons, teams=teams)

@app.route('/api/query5', methods=['POST'])
def api_query5():
    """API endpoint for Query 5"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    team = data.get('team')
    last_n = data.get('last_n', 10)
    
    try:
        # Get all matches for this team
        matches = list(db.matches.find({
            'league_name': league,
            'season': season,
            '$or': [
                {'home_team.name': team},
                {'away_team.name': team}
            ]
        }).sort('date', 1))
        
        if not matches:
            return jsonify({'error': f'No matches found for {team}'}), 404
        
        # Get last N matches
        recent_matches = matches[-last_n:] if len(matches) >= last_n else matches
        
        # Analyze form
        form_string = ""
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        
        match_details = []
        
        for match in recent_matches:
            home = match['home_team']['name']
            away = match['away_team']['name']
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Determine result from team's perspective
            if home == team:
                goals_for += home_goals
                goals_against += away_goals
                if home_goals > away_goals:
                    form_string += "W"
                    wins += 1
                    result = "Win"
                elif home_goals < away_goals:
                    form_string += "L"
                    losses += 1
                    result = "Loss"
                else:
                    form_string += "D"
                    draws += 1
                    result = "Draw"
                opponent = away
                venue = "Home"
                score = f"{home_goals}-{away_goals}"
            else:
                goals_for += away_goals
                goals_against += home_goals
                if away_goals > home_goals:
                    form_string += "W"
                    wins += 1
                    result = "Win"
                elif away_goals < home_goals:
                    form_string += "L"
                    losses += 1
                    result = "Loss"
                else:
                    form_string += "D"
                    draws += 1
                    result = "Draw"
                opponent = home
                venue = "Away"
                score = f"{away_goals}-{home_goals}"
            
            match_details.append({
                'date': match['date'].strftime('%Y-%m-%d') if hasattr(match['date'], 'strftime') else str(match['date'])[:10],
                'opponent': opponent,
                'venue': venue,
                'score': score,
                'result': result
            })
        
        points = wins * 3 + draws
        max_points = len(recent_matches) * 3
        goal_diff = goals_for - goals_against
        
        return jsonify({
            'team': team,
            'matches_analyzed': len(recent_matches),
            'form': form_string,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_diff': goal_diff,
            'points': points,
            'max_points': max_points,
            'matches': match_details
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/query6')
def query6_page():
    """Query 6: Scoring Analysis"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    return render_template('query6.html', leagues=leagues, seasons=seasons)

@app.route('/api/query6', methods=['POST'])
def api_query6():
    """API endpoint for Query 6"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    
    try:
        matches = db.matches.find({
            'league_name': league,
            'season': season
        })
        
        teams = {}
        
        for match in matches:
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Initialize teams
            if home_team not in teams:
                teams[home_team] = {
                    'team': home_team,
                    'matches': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0
                }
            
            if away_team not in teams:
                teams[away_team] = {
                    'team': away_team,
                    'matches': 0,
                    'goals_scored': 0,
                    'goals_conceded': 0
                }
            
            # Update stats
            teams[home_team]['matches'] += 1
            teams[home_team]['goals_scored'] += home_goals
            teams[home_team]['goals_conceded'] += away_goals
            
            teams[away_team]['matches'] += 1
            teams[away_team]['goals_scored'] += away_goals
            teams[away_team]['goals_conceded'] += home_goals
        
        # Calculate averages
        results = []
        for team_data in teams.values():
            avg_scored = round(team_data['goals_scored'] / team_data['matches'], 2)
            avg_conceded = round(team_data['goals_conceded'] / team_data['matches'], 2)
            
            results.append({
                'team': team_data['team'],
                'matches': team_data['matches'],
                'goals_scored': team_data['goals_scored'],
                'goals_conceded': team_data['goals_conceded'],
                'avg_scored': avg_scored,
                'avg_conceded': avg_conceded
            })
        
        # Sort by different criteria
        best_attack = sorted(results, key=lambda x: x['avg_scored'], reverse=True)
        best_defense = sorted(results, key=lambda x: x['avg_conceded'])
        worst_defense = sorted(results, key=lambda x: x['avg_conceded'], reverse=True)
        
        # Summary
        summary = {
            'best_attack': best_attack[0],
            'best_defense': best_defense[0],
            'worst_defense': worst_defense[0]
        }
        
        return jsonify({
            'best_attack': best_attack,
            'best_defense': best_defense,
            'worst_defense': worst_defense,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/query7')
def query7_page():
    """Query 7: Attributes Correlation"""
    leagues = sorted(db.leagues.distinct('name'))
    seasons = sorted(db.matches.distinct('season'), reverse=True)
    return render_template('query7.html', leagues=leagues, seasons=seasons)

@app.route('/api/query7', methods=['POST'])
def api_query7():
    """API endpoint for Query 7"""
    data = request.get_json()
    league = data.get('league')
    season = data.get('season')
    
    try:
        # Get team attributes
        teams_data = {}
        for team in db.teams.find():
            if team.get('attributes_history'):
                latest_attrs = team['attributes_history'][-1]
                teams_data[team['team_api_id']] = {
                    'name': team['team_long_name'],
                    'buildUpPlaySpeed': latest_attrs.get('buildUpPlaySpeed', 50),
                    'defencePressure': latest_attrs.get('defencePressure', 50),
                    'chanceCreationShooting': latest_attrs.get('chanceCreationShooting', 50)
                }
        
        # Analyze matches
        matches = db.matches.find({
            'league_name': league,
            'season': season
        })
        
        analysis = {
            'total_matches': 0,
            'stronger_wins': 0,
            'weaker_wins': 0,
            'draws': 0,
            'rating_buckets': {}
        }
        
        for match in matches:
            home_id = match.get('home_team_api_id')
            away_id = match.get('away_team_api_id')
            
            if home_id not in teams_data or away_id not in teams_data:
                continue
            
            home_attrs = teams_data[home_id]
            away_attrs = teams_data[away_id]
            
            # Calculate overall ratings
            home_rating = (home_attrs['buildUpPlaySpeed'] + 
                          home_attrs['defencePressure'] + 
                          home_attrs['chanceCreationShooting']) / 3
            
            away_rating = (away_attrs['buildUpPlaySpeed'] + 
                          away_attrs['defencePressure'] + 
                          away_attrs['chanceCreationShooting']) / 3
            
            rating_diff = home_rating - away_rating
            
            home_goals = match.get('home_team_goal', 0)
            away_goals = match.get('away_team_goal', 0)
            
            # Determine outcome
            if home_goals > away_goals:
                outcome = 'home_win'
            elif away_goals > home_goals:
                outcome = 'away_win'
            else:
                outcome = 'draw'
            
            # Count results
            analysis['total_matches'] += 1
            
            if outcome == 'draw':
                analysis['draws'] += 1
            elif (outcome == 'home_win' and rating_diff > 0) or \
                 (outcome == 'away_win' and rating_diff < 0):
                analysis['stronger_wins'] += 1
            else:
                analysis['weaker_wins'] += 1
            
            # Bucket by rating difference (5-point intervals)
            bucket = int(rating_diff / 5) * 5
            if bucket not in analysis['rating_buckets']:
                analysis['rating_buckets'][bucket] = {
                    'matches': 0,
                    'stronger_wins': 0,
                    'weaker_wins': 0,
                    'draws': 0
                }
            
            analysis['rating_buckets'][bucket]['matches'] += 1
            
            if outcome == 'draw':
                analysis['rating_buckets'][bucket]['draws'] += 1
            elif (outcome == 'home_win' and rating_diff > 0) or \
                 (outcome == 'away_win' and rating_diff < 0):
                analysis['rating_buckets'][bucket]['stronger_wins'] += 1
            else:
                analysis['rating_buckets'][bucket]['weaker_wins'] += 1
        
        # Calculate percentages
        total = analysis['total_matches']
        stronger_win_pct = round((analysis['stronger_wins'] / total * 100), 1) if total > 0 else 0
        weaker_win_pct = round((analysis['weaker_wins'] / total * 100), 1) if total > 0 else 0
        draw_pct = round((analysis['draws'] / total * 100), 1) if total > 0 else 0
        
        # Format buckets
        buckets = []
        for bucket_val, stats in sorted(analysis['rating_buckets'].items()):
            if stats['matches'] > 0:
                stronger_pct = round((stats['stronger_wins'] / stats['matches'] * 100), 1)
                upset_pct = round((stats['weaker_wins'] / stats['matches'] * 100), 1)
                bucket_draw_pct = round((stats['draws'] / stats['matches'] * 100), 1)
                
                buckets.append({
                    'bucket_range': f"{bucket_val:+d} to {bucket_val+5:+d}",
                    'matches': stats['matches'],
                    'stronger_win_pct': stronger_pct,
                    'upset_pct': upset_pct,
                    'draw_pct': bucket_draw_pct
                })
        
        return jsonify({
            'total_matches': analysis['total_matches'],
            'stronger_wins': analysis['stronger_wins'],
            'weaker_wins': analysis['weaker_wins'],
            'draws': analysis['draws'],
            'stronger_win_pct': stronger_win_pct,
            'weaker_win_pct': weaker_win_pct,
            'draw_pct': draw_pct,
            'buckets': buckets
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Starting Soccer Analytics Web Application")
    print("="*70)
    print("\nOpen your browser and go to: http://localhost:5001")
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)