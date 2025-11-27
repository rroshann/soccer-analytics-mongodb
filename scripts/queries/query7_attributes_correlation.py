"""
Query 7: Team Attributes Correlation with Success
Analyzes if team attributes (FIFA ratings) correlate with match outcomes
This query supports the ML prediction model
"""

from pymongo import MongoClient

def get_attributes_correlation(league_name, season):
    """Analyze correlation between team attributes and match outcomes"""
    
    print(f"\n{'='*70}")
    print(f"Query 7: Team Attributes vs Match Outcomes")
    print(f"League: {league_name}")
    print(f"Season: {season}")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    print("Analyzing team attributes and match results...\n")
    
    # Get all teams with attributes
    teams_data = {}
    for team in db.teams.find():
        if team.get('attributes_history'):
            # Get most recent attributes
            latest_attrs = team['attributes_history'][-1]
            teams_data[team['team_api_id']] = {
                'name': team['team_long_name'],
                'buildUpPlaySpeed': latest_attrs.get('buildUpPlaySpeed', 50),
                'defencePressure': latest_attrs.get('defencePressure', 50),
                'chanceCreationShooting': latest_attrs.get('chanceCreationShooting', 50)
            }
    
    # Analyze matches
    matches = db.matches.find({
        'league_name': league_name,
        'season': season
    })
    
    # Track outcomes based on attribute differences
    analysis = {
        'total_matches': 0,
        'stronger_team_wins': 0,
        'weaker_team_wins': 0,
        'draws': 0,
        'rating_buckets': {}
    }
    
    match_details = []
    
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
        
        # Did the stronger team win?
        analysis['total_matches'] += 1
        
        if outcome == 'draw':
            analysis['draws'] += 1
        elif (outcome == 'home_win' and rating_diff > 0) or \
             (outcome == 'away_win' and rating_diff < 0):
            analysis['stronger_team_wins'] += 1
        else:
            analysis['weaker_team_wins'] += 1
        
        # Bucket by rating difference
        bucket = int(rating_diff / 5) * 5  # Bucket in 5-point intervals
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
        
        match_details.append({
            'home': match['home_team']['name'],
            'away': match['away_team']['name'],
            'home_rating': round(home_rating, 1),
            'away_rating': round(away_rating, 1),
            'rating_diff': round(rating_diff, 1),
            'outcome': outcome,
            'score': f"{home_goals}-{away_goals}"
        })
    
    client.close()
    return analysis, match_details


def print_results(analysis, match_details):
    """Print correlation analysis"""
    
    if not analysis or analysis['total_matches'] == 0:
        print("No results found.")
        return
    
    print("="*70)
    print("OVERALL CORRELATION SUMMARY")
    print("="*70)
    print(f"Total matches analyzed: {analysis['total_matches']}")
    print(f"Stronger team wins: {analysis['stronger_team_wins']} "
          f"({analysis['stronger_team_wins']/analysis['total_matches']*100:.1f}%)")
    print(f"Weaker team wins (upsets): {analysis['weaker_team_wins']} "
          f"({analysis['weaker_team_wins']/analysis['total_matches']*100:.1f}%)")
    print(f"Draws: {analysis['draws']} "
          f"({analysis['draws']/analysis['total_matches']*100:.1f}%)")
    
    print(f"\n{'='*70}")
    print("WIN RATE BY RATING DIFFERENCE")
    print("="*70)
    print(f"{'Rating Diff':<15} {'Matches':<10} {'Stronger Win %':<15} {'Upset %':<12} {'Draw %':<10}")
    print("-" * 70)
    
    # Sort buckets
    sorted_buckets = sorted(analysis['rating_buckets'].items())
    
    for bucket, stats in sorted_buckets:
        if stats['matches'] > 0:
            stronger_pct = stats['stronger_wins'] / stats['matches'] * 100
            weaker_pct = stats['weaker_wins'] / stats['matches'] * 100
            draw_pct = stats['draws'] / stats['matches'] * 100
            
            bucket_str = f"{bucket:+.0f} to {bucket+5:+.0f}"
            print(f"{bucket_str:<15} {stats['matches']:<10} {stronger_pct:<15.1f} "
                  f"{weaker_pct:<12.1f} {draw_pct:<10.1f}")
    
    print("\n")


if __name__ == "__main__":
    league = "England Premier League"
    season = "2015/2016"
    
    analysis, match_details = get_attributes_correlation(league, season)
    print_results(analysis, match_details)
    
    if analysis:
        stronger_win_rate = analysis['stronger_team_wins'] / analysis['total_matches'] * 100
        
        print(f"Key Finding: Team attributes predict winners {stronger_win_rate:.1f}% of the time")
        print(f"This validates using attributes as features for ML prediction!\n")