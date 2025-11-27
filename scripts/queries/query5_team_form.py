"""
Query 5: Team Form Analysis
Shows recent performance trends (last N games)
"""

from pymongo import MongoClient
from datetime import datetime

def get_team_form(team_name, league_name, season, last_n=5):
    """Get recent form for a specific team"""
    
    print(f"\n{'='*70}")
    print(f"Query 5: Team Form Analysis")
    print(f"Team: {team_name}")
    print(f"League: {league_name}")
    print(f"Season: {season}")
    print(f"Last {last_n} matches")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    # Get all matches for this team
    matches = list(db.matches.find({
        'league_name': league_name,
        'season': season,
        '$or': [
            {'home_team.name': team_name},
            {'away_team.name': team_name}
        ]
    }).sort('date', 1))
    
    if not matches:
        print(f"No matches found for {team_name}")
        client.close()
        return None
    
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
        if home == team_name:
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
        
        match_details.append({
            'date': match['date'],
            'opponent': opponent,
            'venue': venue,
            'score': f"{home_goals}-{away_goals}",
            'result': result
        })
    
    points = wins * 3 + draws
    max_points = len(recent_matches) * 3
    
    summary = {
        'team': team_name,
        'matches_analyzed': len(recent_matches),
        'form': form_string,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'goal_diff': goals_for - goals_against,
        'points': points,
        'max_points': max_points,
        'matches': match_details
    }
    
    client.close()
    return summary


def get_all_teams_form(league_name, season, last_n=5):
    """Get form for all teams in league"""
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    # Get all unique teams
    teams = db.matches.distinct('home_team.name', {
        'league_name': league_name,
        'season': season
    })
    
    all_forms = []
    
    for team in teams:
        form = get_team_form(team, league_name, season, last_n)
        if form:
            all_forms.append(form)
    
    # Sort by points in last N games
    all_forms.sort(key=lambda x: (x['points'], x['goal_diff']), reverse=True)
    
    return all_forms


def print_results(summary):
    """Print team form analysis"""
    
    if not summary:
        return
    
    print(f"\n{'='*70}")
    print("FORM SUMMARY")
    print(f"{'='*70}")
    print(f"Form: {summary['form']} (W=Win, D=Draw, L=Loss)")
    print(f"Record: {summary['wins']}W - {summary['draws']}D - {summary['losses']}L")
    print(f"Points: {summary['points']}/{summary['max_points']}")
    print(f"Goals: {summary['goals_for']} scored, {summary['goals_against']} conceded (Diff: {summary['goal_diff']:+d})")
    
    print(f"\n{'='*70}")
    print("MATCH DETAILS")
    print(f"{'='*70}")
    print(f"{'Date':<12} {'Opponent':<30} {'Venue':<8} {'Score':<8} {'Result':<8}")
    print("-" * 70)
    
    for match in summary['matches']:
        date_str = match['date'].strftime('%Y-%m-%d') if isinstance(match['date'], datetime) else str(match['date'])[:10]
        print(f"{date_str:<12} {match['opponent']:<30} {match['venue']:<8} {match['score']:<8} {match['result']:<8}")
    
    print("\n")


if __name__ == "__main__":
    # Example 1: Single team form
    team = "Leicester City"
    league = "England Premier League"
    season = "2015/2016"
    
    form = get_team_form(team, league, season, last_n=10)
    print_results(form)
    
    # Example 2: All teams current form (last 5 games)
    print("\n" + "="*70)
    print("LEAGUE FORM TABLE (Last 5 Games)")
    print("="*70)
    
    all_forms = get_all_teams_form(league, season, last_n=5)
    
    print(f"\n{'Pos':<5} {'Team':<30} {'Form':<8} {'Pts':<5} {'GD':<6}")
    print("-" * 60)
    
    for i, team_form in enumerate(all_forms[:10], 1):
        print(f"{i:<5} {team_form['team']:<30} {team_form['form']:<8} "
              f"{team_form['points']:<5} {team_form['goal_diff']:>+5}")
    
    print("\n")