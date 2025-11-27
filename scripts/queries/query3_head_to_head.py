"""
Query 3: Head-to-Head Historical Record
Shows all matches and statistics between two specific teams
"""

from pymongo import MongoClient
from datetime import datetime

def get_head_to_head(team1, team2, league_name=None):
    """Get head-to-head record between two teams"""
    
    print(f"\n{'='*70}")
    print(f"Query 3: Head-to-Head Record")
    print(f"{team1} vs {team2}")
    if league_name:
        print(f"League: {league_name}")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    # Build query
    query = {
        '$or': [
            {'home_team.name': team1, 'away_team.name': team2},
            {'home_team.name': team2, 'away_team.name': team1}
        ]
    }
    
    if league_name:
        query['league_name'] = league_name
    
    # Get all matches between these teams
    matches = list(db.matches.find(query).sort('date', 1))
    
    if not matches:
        print(f"No matches found between {team1} and {team2}")
        client.close()
        return None
    
    # Calculate statistics
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
            'date': match['date'],
            'season': match['season'],
            'home': home,
            'away': away,
            'score': f"{home_goals}-{away_goals}",
            'result': result,
            'league': match.get('league_name', 'Unknown')
        })
    
    summary = {
        'team1': team1,
        'team2': team2,
        'total_matches': len(matches),
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'draws': draws,
        'team1_goals': team1_goals,
        'team2_goals': team2_goals,
        'matches': match_details
    }
    
    client.close()
    return summary


def print_results(summary):
    """Print head-to-head results"""
    
    if not summary:
        return
    
    # Print summary stats
    print(f"\n{'='*70}")
    print("OVERALL RECORD")
    print(f"{'='*70}")
    print(f"Total matches: {summary['total_matches']}")
    print(f"{summary['team1']} wins: {summary['team1_wins']}")
    print(f"{summary['team2']} wins: {summary['team2_wins']}")
    print(f"Draws: {summary['draws']}")
    print(f"Goals: {summary['team1']} {summary['team1_goals']} - {summary['team2_goals']} {summary['team2']}")
    
    team1_win_pct = (summary['team1_wins'] / summary['total_matches'] * 100)
    team2_win_pct = (summary['team2_wins'] / summary['total_matches'] * 100)
    
    print(f"\nWin percentage: {summary['team1']} {team1_win_pct:.1f}% - {team2_win_pct:.1f}% {summary['team2']}")
    
    # Print recent matches
    print(f"\n{'='*70}")
    print("RECENT MATCHES (Last 10)")
    print(f"{'='*70}")
    print(f"{'Date':<12} {'Season':<12} {'Home':<25} {'Score':<8} {'Away':<25} {'Result':<15}")
    print("-" * 110)
    
    recent = summary['matches'][-10:]
    for match in reversed(recent):
        date_str = match['date'].strftime('%Y-%m-%d') if isinstance(match['date'], datetime) else str(match['date'])[:10]
        print(f"{date_str:<12} {match['season']:<12} {match['home']:<25} {match['score']:<8} "
              f"{match['away']:<25} {match['result']:<15}")
    
    print("\n")


if __name__ == "__main__":
    # Example: Manchester United vs Liverpool rivalry
    team1 = "Manchester United"
    team2 = "Liverpool"
    
    summary = get_head_to_head(team1, team2, league_name="England Premier League")
    print_results(summary)