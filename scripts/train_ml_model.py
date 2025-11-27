"""
Train Machine Learning Model for Match Outcome Prediction
Uses team attributes to predict Win/Draw/Loss
"""

from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

def extract_features_from_mongodb():
    """Extract match data with team attributes for ML training"""
    
    print("Connecting to MongoDB...")
    client = MongoClient('mongodb://localhost:27017/')
    db = client['soccer_analytics']
    
    print("Loading team attributes...")
    teams_attrs = {}
    for team in db.teams.find():
        if team.get('attributes_history'):
            latest = team['attributes_history'][-1]
            teams_attrs[team['team_api_id']] = {
                'buildUpPlaySpeed': latest.get('buildUpPlaySpeed', 50),
                'defencePressure': latest.get('defencePressure', 50),
                'chanceCreationShooting': latest.get('chanceCreationShooting', 50),
                'defenceAggression': latest.get('defenceAggression', 50)
            }
    
    print("Loading matches...")
    matches = list(db.matches.find())
    
    print(f"Processing {len(matches)} matches...")
    
    data = []
    
    for match in matches:
        home_id = match.get('home_team_api_id')
        away_id = match.get('away_team_api_id')
        
        if home_id not in teams_attrs or away_id not in teams_attrs:
            continue
        
        home_attrs = teams_attrs[home_id]
        away_attrs = teams_attrs[away_id]
        
        # Calculate ratings
        home_rating = (home_attrs['buildUpPlaySpeed'] + 
                      home_attrs['defencePressure'] + 
                      home_attrs['chanceCreationShooting']) / 3
        
        away_rating = (away_attrs['buildUpPlaySpeed'] + 
                      away_attrs['defencePressure'] + 
                      away_attrs['chanceCreationShooting']) / 3
        
        # Features
        features = {
            'home_rating': home_rating,
            'away_rating': away_rating,
            'rating_diff': home_rating - away_rating,
            'home_build_up': home_attrs['buildUpPlaySpeed'],
            'away_build_up': away_attrs['buildUpPlaySpeed'],
            'home_defense': home_attrs['defencePressure'],
            'away_defense': away_attrs['defencePressure'],
            'home_attack': home_attrs['chanceCreationShooting'],
            'away_attack': away_attrs['chanceCreationShooting'],
            'attack_diff': home_attrs['chanceCreationShooting'] - away_attrs['chanceCreationShooting'],
            'defense_diff': home_attrs['defencePressure'] - away_attrs['defencePressure'],
            'home_advantage': 1
        }
        
        # Target (outcome)
        home_goals = match.get('home_team_goal', 0)
        away_goals = match.get('away_team_goal', 0)
        
        if home_goals > away_goals:
            outcome = 2  # Home win
        elif away_goals > home_goals:
            outcome = 0  # Away win
        else:
            outcome = 1  # Draw
        
        features['outcome'] = outcome
        data.append(features)
    
    df = pd.DataFrame(data)
    
    print(f"Created dataset with {len(df)} matches")
    
    client.close()
    return df


def train_model():
    """Train the prediction model"""
    
    print("\n" + "="*70)
    print("TRAINING MATCH OUTCOME PREDICTION MODEL")
    print("="*70 + "\n")
    
    # Extract data
    df = extract_features_from_mongodb()
    
    # Separate features and target
    X = df.drop('outcome', axis=1)
    y = df['outcome']
    
    print(f"Dataset: {len(X)} matches")
    print(f"Features: {list(X.columns)}")
    print(f"\nOutcome distribution:")
    print(f"  Away Win (0): {sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")
    print(f"  Draw (1): {sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%)")
    print(f"  Home Win (2): {sum(y==2)} ({sum(y==2)/len(y)*100:.1f}%)")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} matches")
    print(f"Test set: {len(X_test)} matches")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE")
    print("="*70)
    print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['Away Win', 'Draw', 'Home Win'],
                                digits=3))
    
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("              Predicted")
    print("              Away  Draw  Home")
    print(f"Actual Away   {cm[0][0]:4d}  {cm[0][1]:4d}  {cm[0][2]:4d}")
    print(f"       Draw   {cm[1][0]:4d}  {cm[1][1]:4d}  {cm[1][2]:4d}")
    print(f"       Home   {cm[2][0]:4d}  {cm[2][1]:4d}  {cm[2][2]:4d}")
    
    # Feature importance
    print("\nFeature Importance:")
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for _, row in importance_df.iterrows():
        print(f"  {row['feature']:<20} {row['importance']:.4f}")
    
    # Save model
    print("\nSaving model...")
    
    # Create data/model directory if it doesn't exist
    os.makedirs('../data/model', exist_ok=True)
    
    model_data = {
        'model': model,
        'scaler': scaler,
        'features': list(X.columns)
    }
    
    with open('../data/model/rf_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Model saved to: ../data/model/rf_model.pkl")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"\nModel Accuracy: {accuracy*100:.2f}%")
    print("Note: 50-60% accuracy is typical for soccer prediction")
    print("The model can now be used for match predictions!\n")


if __name__ == "__main__":
    train_model()