"""
Query 2: Home vs Away Performance Analysis
Shows how teams perform at home vs away
"""

from pymongo import MongoClient

def get_home_away_performance(league_name, season):
    """Analyze home vs away performance for all teams"""
    
    print(f"\n{'='*70}")
    print(f"Query 2: Home vs Away Performance")
    print(f"League: {league_name}")
    print(f"Season: {season}")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    matches = db.matches.find({
        'league_name': league_name,
        'season': season
    })
    
    teams = {}
    
    print("Analyzing home and away records...\n")
    
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
    
    # Calculate win percentages and home advantage
    results = []
    for team_data in teams.values():
        home_win_pct = (team_data['home_wins'] / team_data['home_played'] * 100) if team_data['home_played'] > 0 else 0
        away_win_pct = (team_data['away_wins'] / team_data['away_played'] * 100) if team_data['away_played'] > 0 else 0
        home_advantage = home_win_pct - away_win_pct
        
        results.append({
            'team': team_data['team'],
            'home_wins': team_data['home_wins'],
            'home_played': team_data['home_played'],
            'home_win_pct': round(home_win_pct, 1),
            'away_wins': team_data['away_wins'],
            'away_played': team_data['away_played'],
            'away_win_pct': round(away_win_pct, 1),
            'home_advantage': round(home_advantage, 1),
            'home_points': team_data['home_points'],
            'away_points': team_data['away_points']
        })
    
    # Sort by home advantage
    results.sort(key=lambda x: x['home_advantage'], reverse=True)
    
    client.close()
    return results


def print_results(results):
    """Print home vs away comparison"""
    
    if not results:
        print("No results found.")
        return
    
    print(f"{'Team':<30} {'Home W%':<10} {'Away W%':<10} {'Advantage':<12} {'H Pts':<8} {'A Pts':<8}")
    print("-" * 85)
    
    for team in results:
        print(f"{team['team']:<30} {team['home_win_pct']:<10} {team['away_win_pct']:<10} "
              f"{team['home_advantage']:>+10.1f}% {team['home_points']:<8} {team['away_points']:<8}")
    
    print("\n")


if __name__ == "__main__":
    league = "England Premier League"
    season = "2015/2016"
    
    results = get_home_away_performance(league, season)
    print_results(results)
    
    if results:
        best_home = results[0]
        worst_home = results[-1]
        
        print(f"Biggest home advantage: {best_home['team']} (+{best_home['home_advantage']}%)")
        print(f"Smallest home advantage: {worst_home['team']} ({worst_home['home_advantage']:+.1f}%)")
        
        avg_advantage = sum(r['home_advantage'] for r in results) / len(results)
        print(f"League average home advantage: {avg_advantage:+.1f}%\n")