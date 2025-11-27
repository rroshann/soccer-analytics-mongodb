"""
Query 4: Player Appearance Frequency
Shows most frequently appearing players by league/season
"""

from pymongo import MongoClient

def get_player_appearances(league_name, season, limit=15):
    """Get players with most appearances"""
    
    print(f"\n{'='*70}")
    print(f"Query 4: Player Appearance Frequency")
    print(f"League: {league_name}")
    print(f"Season: {season}")
    print(f"{'='*70}\n")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    matches = db.matches.find({
        'league_name': league_name,
        'season': season
    })
    
    player_stats = {}
    
    print("Counting player appearances...\n")
    
    for match in matches:
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
    
    client.close()
    return top_players


def print_results(players):
    """Print player appearance stats"""
    
    if not players:
        print("No results found.")
        return
    
    print(f"{'Rank':<6} {'Player':<30} {'Appearances':<15} {'Team(s)':<30}")
    print("-" * 85)
    
    for i, player in enumerate(players, 1):
        print(f"{i:<6} {player['player']:<30} {player['appearances']:<15} {player['teams']:<30}")
    
    print("\n")


if __name__ == "__main__":
    league = "England Premier League"
    season = "2015/2016"
    
    players = get_player_appearances(league, season, limit=15)
    print_results(players)
    
    if players:
        iron_man = players[0]
        print(f"Most appearances: {iron_man['player']} with {iron_man['appearances']} games")
        
        # Count players with 30+ appearances (regular starters)
        regulars = sum(1 for p in players if p['appearances'] >= 30)
        print(f"Players with 30+ appearances: {regulars}\n")