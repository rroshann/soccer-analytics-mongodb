"""
Query 1: Team Performance by Season
Calculates wins, draws, losses, goals, and points for each team
"""

from pymongo import MongoClient

def get_team_performance(league_name, season):
    """Get team performance statistics for a league and season"""
    
    print(f"\n{'='*70}")
    print(f"Query 1: Team Performance Analysis")
    print(f"League: {league_name}")
    print(f"Season: {season}")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    # Get all matches for this league and season
    matches = db.matches.find({
        'league_name': league_name,
        'season': season
    })
    
    teams = {}
    
    print("Analyzing matches...\n")
    
    for match in matches:
        home_team = match['home_team']['name']
        away_team = match['away_team']['name']
        home_goals = match.get('home_team_goal', 0)
        away_goals = match.get('away_team_goal', 0)
        
        # Initialize teams if not seen before
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
        
        # Update home team stats
        teams[home_team]['played'] += 1
        teams[home_team]['goals_for'] += home_goals
        teams[home_team]['goals_against'] += away_goals
        
        # Update away team stats
        teams[away_team]['played'] += 1
        teams[away_team]['goals_for'] += away_goals
        teams[away_team]['goals_against'] += home_goals
        
        # Determine result
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
    
    # Sort by points, then goal difference
    standings = sorted(teams.values(), 
                      key=lambda x: (x['points'], x['goal_diff']), 
                      reverse=True)
    
    client.close()
    return standings


def print_results(standings):
    """Print league table"""
    
    if not standings:
        print("No results found.")
        return
    
    print(f"{'Pos':<4} {'Team':<30} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<5} {'GA':<5} {'GD':<6} {'Pts':<5}")
    print("-" * 85)
    
    for i, team in enumerate(standings, 1):
        print(f"{i:<4} {team['team']:<30} {team['played']:<4} {team['wins']:<4} "
              f"{team['draws']:<4} {team['losses']:<4} {team['goals_for']:<5} "
              f"{team['goals_against']:<5} {team['goal_diff']:<6} {team['points']:<5}")
    
    print("\n")


if __name__ == "__main__":
    # Test with Premier League 2015/2016
    league = "England Premier League"
    season = "2015/2016"
    
    standings = get_team_performance(league, season)
    print_results(standings)
    
    if standings:
        print(f"Champion: {standings[0]['team']} with {standings[0]['points']} points")
        print(f"Top scorer (team): {max(standings, key=lambda x: x['goals_for'])['team']}")
        print(f"Best defense: {min(standings, key=lambda x: x['goals_against'])['team']}\n")