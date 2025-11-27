import sqlite3
from pymongo import MongoClient
from datetime import datetime
import sys

def connect_sqlite(db_path='./database.sqlite'):
    """Connect to SQLite database"""
    print(f"Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def connect_mongo(uri='mongodb://localhost:27017/', db_name='soccer_analytics'):
    """Connect to MongoDB"""
    print(f"Connecting to MongoDB: {uri}")
    client = MongoClient(uri)
    return client[db_name]

def dict_from_row(row):
    """Convert SQLite row to dictionary"""
    return {k: row[k] for k in row.keys()}

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return date_str

def convert_leagues_and_countries(sqlite_conn, mongo_db):
    """Import leagues and countries"""
    print("\n=== Converting Countries and Leagues ===")
    
    # Get countries first
    cursor = sqlite_conn.execute("SELECT * FROM Country")
    countries = [dict_from_row(row) for row in cursor.fetchall()]
    print(f"Found {len(countries)} countries")
    
    # Get leagues with country names
    cursor = sqlite_conn.execute("""
        SELECT l.*, c.name as country_name 
        FROM League l
        LEFT JOIN Country c ON l.country_id = c.id
    """)
    leagues = []
    for row in cursor.fetchall():
        league_doc = dict_from_row(row)
        leagues.append(league_doc)
    
    if leagues:
        mongo_db.leagues.insert_many(leagues)
        print(f"✓ Imported {len(leagues)} leagues")
    else:
        print("✗ No leagues found")

def convert_teams(sqlite_conn, mongo_db):
    """Import teams with embedded attributes"""
    print("\n=== Converting Teams ===")
    
    # Get all teams
    cursor = sqlite_conn.execute("SELECT * FROM Team")
    teams_dict = {}
    for row in cursor.fetchall():
        team = dict_from_row(row)
        team['attributes_history'] = []
        teams_dict[team['team_api_id']] = team
    
    print(f"Found {len(teams_dict)} teams")
    
    # Get team attributes
    cursor = sqlite_conn.execute("SELECT * FROM Team_Attributes ORDER BY date")
    attr_count = 0
    for row in cursor.fetchall():
        attr = dict_from_row(row)
        team_api_id = attr.get('team_api_id')
        if team_api_id and team_api_id in teams_dict:
            attr['date'] = parse_date(attr.get('date'))
            teams_dict[team_api_id]['attributes_history'].append(attr)
            attr_count += 1
    
    print(f"Found {attr_count} team attribute records")
    
    teams_list = list(teams_dict.values())
    if teams_list:
        mongo_db.teams.insert_many(teams_list)
        print(f"✓ Imported {len(teams_list)} teams with attributes")
    else:
        print("✗ No teams found")

def convert_players(sqlite_conn, mongo_db):
    """Import players with embedded attributes"""
    print("\n=== Converting Players ===")
    
    # Get all players
    cursor = sqlite_conn.execute("SELECT * FROM Player")
    players_dict = {}
    for row in cursor.fetchall():
        player = dict_from_row(row)
        player['attributes_history'] = []
        players_dict[player['player_api_id']] = player
    
    print(f"Found {len(players_dict)} players")
    
    # Get player attributes
    cursor = sqlite_conn.execute("SELECT * FROM Player_Attributes ORDER BY date")
    attr_count = 0
    for row in cursor.fetchall():
        attr = dict_from_row(row)
        player_api_id = attr.get('player_api_id')
        if player_api_id and player_api_id in players_dict:
            attr['date'] = parse_date(attr.get('date'))
            players_dict[player_api_id]['attributes_history'].append(attr)
            attr_count += 1
    
    print(f"Found {attr_count} player attribute records")
    
    players_list = list(players_dict.values())
    if players_list:
        # Insert in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(players_list), batch_size):
            batch = players_list[i:i+batch_size]
            mongo_db.players.insert_many(batch)
            print(f"  Inserted {min(i+batch_size, len(players_list))}/{len(players_list)} players...")
        print(f"✓ Imported {len(players_list)} players with attributes")
    else:
        print("✗ No players found")

def convert_matches(sqlite_conn, mongo_db):
    """Import matches with denormalized team and player info"""
    print("\n=== Converting Matches ===")
    
    # Get teams lookup
    print("Building team lookup...")
    teams_lookup = {}
    for team in mongo_db.teams.find():
        teams_lookup[team['team_api_id']] = team
    print(f"Loaded {len(teams_lookup)} teams")
    
    # Get players lookup
    print("Building player lookup...")
    players_lookup = {}
    for player in mongo_db.players.find():
        players_lookup[player['player_api_id']] = player
    print(f"Loaded {len(players_lookup)} players")
    
    # Get matches with league and country info
    cursor = sqlite_conn.execute("""
        SELECT 
            m.*,
            l.name as league_name,
            c.name as country_name
        FROM Match m
        LEFT JOIN League l ON m.league_id = l.id
        LEFT JOIN Country c ON m.country_id = c.id
    """)
    
    matches = []
    match_count = 0
    
    print("Converting match records...")
    for row in cursor.fetchall():
        match_doc = dict_from_row(row)
        
        # Parse date
        if match_doc.get('date'):
            match_doc['date'] = parse_date(match_doc['date'])
        
        # Embed home team info
        home_team_api_id = match_doc.get('home_team_api_id')
        if home_team_api_id and home_team_api_id in teams_lookup:
            team = teams_lookup[home_team_api_id]
            match_doc['home_team'] = {
                'api_id': home_team_api_id,
                'name': team.get('team_long_name'),
                'short_name': team.get('team_short_name')
            }
        else:
            match_doc['home_team'] = {
                'api_id': home_team_api_id,
                'name': 'Unknown',
                'short_name': 'UNK'
            }
        
        # Embed away team info
        away_team_api_id = match_doc.get('away_team_api_id')
        if away_team_api_id and away_team_api_id in teams_lookup:
            team = teams_lookup[away_team_api_id]
            match_doc['away_team'] = {
                'api_id': away_team_api_id,
                'name': team.get('team_long_name'),
                'short_name': team.get('team_short_name')
            }
        else:
            match_doc['away_team'] = {
                'api_id': away_team_api_id,
                'name': 'Unknown',
                'short_name': 'UNK'
            }
        
        # Embed home lineup (player names) - using home_player_1 through home_player_11
        match_doc['home_lineup'] = []
        for i in range(1, 12):
            player_api_id = match_doc.get(f'home_player_{i}')
            if player_api_id and player_api_id in players_lookup:
                player = players_lookup[player_api_id]
                match_doc['home_lineup'].append({
                    'player_api_id': player_api_id,
                    'player_name': player.get('player_name'),
                    'position': i
                })
        
        # Embed away lineup (player names) - using away_player_1 through away_player_11
        match_doc['away_lineup'] = []
        for i in range(1, 12):
            player_api_id = match_doc.get(f'away_player_{i}')
            if player_api_id and player_api_id in players_lookup:
                player = players_lookup[player_api_id]
                match_doc['away_lineup'].append({
                    'player_api_id': player_api_id,
                    'player_name': player.get('player_name'),
                    'position': i
                })
        
        matches.append(match_doc)
        match_count += 1
        
        # Batch insert every 1000 matches
        if len(matches) >= 1000:
            mongo_db.matches.insert_many(matches)
            print(f"  Inserted {match_count} matches so far...")
            matches = []
    
    # Insert remaining matches
    if matches:
        mongo_db.matches.insert_many(matches)
    
    total_matches = mongo_db.matches.count_documents({})
    print(f"✓ Total matches imported: {total_matches}")

def create_indexes(mongo_db):
    """Create indexes for optimized queries"""
    print("\n=== Creating Indexes ===")
    
    try:
        # Match indexes
        mongo_db.matches.create_index([("date", 1)])
        mongo_db.matches.create_index([("league_id", 1)])
        mongo_db.matches.create_index([("season", 1)])
        mongo_db.matches.create_index([("home_team.name", 1)])
        mongo_db.matches.create_index([("away_team.name", 1)])
        mongo_db.matches.create_index([("league_name", 1)])
        mongo_db.matches.create_index([("home_team_api_id", 1)])
        mongo_db.matches.create_index([("away_team_api_id", 1)])
        print("  ✓ Match indexes created")
        
        # Player indexes
        mongo_db.players.create_index([("player_name", 1)])
        mongo_db.players.create_index([("player_api_id", 1)])
        print("  ✓ Player indexes created")
        
        # Team indexes
        mongo_db.teams.create_index([("team_long_name", 1)])
        mongo_db.teams.create_index([("team_api_id", 1)])
        print("  ✓ Team indexes created")
        
        # League indexes
        mongo_db.leagues.create_index([("name", 1)])
        print("  ✓ League indexes created")
        
        print("✓ All indexes created successfully")
    except Exception as e:
        print(f"Warning: Error creating indexes: {e}")

def main():
    """Main conversion process"""
    print("=" * 60)
    print("SQLite to MongoDB Conversion Script")
    print("European Soccer Database")
    print("=" * 60)
    
    try:
        # Connect to databases
        sqlite_conn = connect_sqlite()
        mongo_db = connect_mongo()
        
        # Drop existing collections for clean import
        print("\nDropping existing collections...")
        mongo_db.leagues.drop()
        mongo_db.teams.drop()
        mongo_db.players.drop()
        mongo_db.matches.drop()
        print("✓ Collections cleared")
        
        # Convert data in order (leagues first, then teams, players, matches)
        convert_leagues_and_countries(sqlite_conn, mongo_db)
        convert_teams(sqlite_conn, mongo_db)
        convert_players(sqlite_conn, mongo_db)
        convert_matches(sqlite_conn, mongo_db)
        
        # Create indexes
        create_indexes(mongo_db)
        
        # Print summary
        print("\n" + "=" * 60)
        print("CONVERSION SUMMARY")
        print("=" * 60)
        print(f"Leagues:  {mongo_db.leagues.count_documents({})}")
        print(f"Teams:    {mongo_db.teams.count_documents({})}")
        print(f"Players:  {mongo_db.players.count_documents({})}")
        print(f"Matches:  {mongo_db.matches.count_documents({})}")
        print("=" * 60)
        print("\n✓ Conversion complete!")
        print("\nYou can now connect to MongoDB and run queries!")
        print("Database name: soccer_analytics")
        print("Collections: leagues, teams, players, matches")
        
        # Close connections
        sqlite_conn.close()
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()