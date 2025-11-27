"""
Query 6: High-Scoring and Low-Scoring Teams Analysis
Offensive vs defensive team classification
"""

from pymongo import MongoClient

def get_scoring_analysis(league_name, season):
    """Analyze offensive and defensive capabilities of teams"""
    
    print(f"\n{'='*70}")
    print(f"Query 6: Scoring Analysis")
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
    
    print("Analyzing offensive and defensive performance...\n")
    
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
        avg_scored = team_data['goals_scored'] / team_data['matches']
        avg_conceded = team_data['goals_conceded'] / team_data['matches']
        
        results.append({
            'team': team_data['team'],
            'matches': team_data['matches'],
            'goals_scored': team_data['goals_scored'],
            'goals_conceded': team_data['goals_conceded'],
            'avg_scored': round(avg_scored, 2),
            'avg_conceded': round(avg_conceded, 2),
            'goal_diff': team_data['goals_scored'] - team_data['goals_conceded']
        })
    
    client.close()
    return results


def print_results(results):
    """Print scoring analysis"""
    
    if not results:
        print("No results found.")
        return
    
    # Sort by goals scored
    by_attack = sorted(results, key=lambda x: x['avg_scored'], reverse=True)
    
    print("="*70)
    print("MOST OFFENSIVE TEAMS (Goals Scored Per Game)")
    print("="*70)
    print(f"{'Rank':<6} {'Team':<30} {'Total':<8} {'Avg/Game':<10}")
    print("-" * 60)
    
    for i, team in enumerate(by_attack[:10], 1):
        print(f"{i:<6} {team['team']:<30} {team['goals_scored']:<8} {team['avg_scored']:<10}")
    
    # Sort by goals conceded (ascending - fewer is better)
    by_defense = sorted(results, key=lambda x: x['avg_conceded'])
    
    print(f"\n{'='*70}")
    print("BEST DEFENSIVE TEAMS (Goals Conceded Per Game)")
    print("="*70)
    print(f"{'Rank':<6} {'Team':<30} {'Total':<8} {'Avg/Game':<10}")
    print("-" * 60)
    
    for i, team in enumerate(by_defense[:10], 1):
        print(f"{i:<6} {team['team']:<30} {team['goals_conceded']:<8} {team['avg_conceded']:<10}")
    
    # Worst defense
    by_worst_defense = sorted(results, key=lambda x: x['avg_conceded'], reverse=True)
    
    print(f"\n{'='*70}")
    print("WORST DEFENSIVE TEAMS (Goals Conceded Per Game)")
    print("="*70)
    print(f"{'Rank':<6} {'Team':<30} {'Total':<8} {'Avg/Game':<10}")
    print("-" * 60)
    
    for i, team in enumerate(by_worst_defense[:5], 1):
        print(f"{i:<6} {team['team']:<30} {team['goals_conceded']:<8} {team['avg_conceded']:<10}")
    
    print("\n")


if __name__ == "__main__":
    league = "England Premier League"
    season = "2015/2016"
    
    results = get_scoring_analysis(league, season)
    print_results(results)
    
    if results:
        best_attack = max(results, key=lambda x: x['avg_scored'])
        best_defense = min(results, key=lambda x: x['avg_conceded'])
        worst_defense = max(results, key=lambda x: x['avg_conceded'])
        
        print(f"Best attack: {best_attack['team']} ({best_attack['avg_scored']} goals/game)")
        print(f"Best defense: {best_defense['team']} ({best_defense['avg_conceded']} goals/game)")
        print(f"Worst defense: {worst_defense['team']} ({worst_defense['avg_conceded']} goals/game)\n")