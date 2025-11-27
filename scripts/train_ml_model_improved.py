"""
Improved ML Model with Multiple Algorithms and Class Balancing
"""

from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

def extract_features_with_form():
    """Extract features including recent form"""
    
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
    
    print("Loading and sorting matches by date...")
    matches = list(db.matches.find().sort('date', 1))
    
    # Track team form (last 5 games)
    team_form = {}  # team_id -> list of recent results (1 for win, 0.5 for draw, 0 for loss)
    
    data = []
    
    print(f"Processing {len(matches)} matches with form calculation...")
    
    for match in matches:
        home_id = match.get('home_team_api_id')
        away_id = match.get('away_team_api_id')
        
        if home_id not in teams_attrs or away_id not in teams_attrs:
            continue
        
        # Initialize form tracking
        if home_id not in team_form:
            team_form[home_id] = []
        if away_id not in team_form:
            team_form[away_id] = []
        
        # Get recent form (last 5 games)
        home_form = sum(team_form[home_id][-5:]) / 5 if team_form[home_id] else 0.5
        away_form = sum(team_form[away_id][-5:]) / 5 if team_form[away_id] else 0.5
        
        home_attrs = teams_attrs[home_id]
        away_attrs = teams_attrs[away_id]
        
        # Calculate ratings
        home_rating = (home_attrs['buildUpPlaySpeed'] + 
                      home_attrs['defencePressure'] + 
                      home_attrs['chanceCreationShooting']) / 3
        
        away_rating = (away_attrs['buildUpPlaySpeed'] + 
                      away_attrs['defencePressure'] + 
                      away_attrs['chanceCreationShooting']) / 3
        
        # Features (including form)
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
            'home_advantage': 1,
            'home_form': home_form,
            'away_form': away_form,
            'form_diff': home_form - away_form
        }
        
        # Target
        home_goals = match.get('home_team_goal', 0)
        away_goals = match.get('away_team_goal', 0)
        
        if home_goals > away_goals:
            outcome = 2  # Home win
            home_result = 1.0
            away_result = 0.0
        elif away_goals > home_goals:
            outcome = 0  # Away win
            home_result = 0.0
            away_result = 1.0
        else:
            outcome = 1  # Draw
            home_result = 0.5
            away_result = 0.5
        
        features['outcome'] = outcome
        data.append(features)
        
        # Update form tracking
        team_form[home_id].append(home_result)
        team_form[away_id].append(away_result)
    
    df = pd.DataFrame(data)
    
    print(f"Created dataset with {len(df)} matches (with form features)")
    
    client.close()
    return df


def train_multiple_models():
    """Train and compare multiple models"""
    
    print("\n" + "="*70)
    print("IMPROVED MODEL TRAINING - COMPARING ALGORITHMS")
    print("="*70 + "\n")
    
    # Extract data with form
    df = extract_features_with_form()
    
    X = df.drop('outcome', axis=1)
    y = df['outcome']
    
    print(f"Dataset: {len(X)} matches")
    print(f"Features: {list(X.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models to test
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }
    
    results = {}
    
    print("\nTraining and evaluating models...\n")
    print("="*70)
    
    for name, model in models.items():
        print(f"\n{name}:")
        print("-" * 70)
        
        # Train
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Detailed metrics
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Away Win', 'Draw', 'Home Win'],
                                    digits=3))
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'predictions': y_pred
        }
    
    # Find best model
    best_name = max(results, key=lambda k: results[k]['accuracy'])
    best_model = results[best_name]['model']
    best_accuracy = results[best_name]['accuracy']
    
    print("\n" + "="*70)
    print("BEST MODEL")
    print("="*70)
    print(f"{best_name}: {best_accuracy*100:.2f}% accuracy")
    
    # Confusion matrix for best model
    y_pred_best = results[best_name]['predictions']
    cm = confusion_matrix(y_test, y_pred_best)
    
    print("\nConfusion Matrix (Best Model):")
    print("              Predicted")
    print("              Away  Draw  Home")
    print(f"Actual Away   {cm[0][0]:4d}  {cm[0][1]:4d}  {cm[0][2]:4d}")
    print(f"       Draw   {cm[1][0]:4d}  {cm[1][1]:4d}  {cm[1][2]:4d}")
    print(f"       Home   {cm[2][0]:4d}  {cm[2][1]:4d}  {cm[2][2]:4d}")
    
    # Feature importance (if available)
    if hasattr(best_model, 'feature_importances_'):
        print("\nFeature Importance:")
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for _, row in importance_df.head(10).iterrows():
            print(f"  {row['feature']:<20} {row['importance']:.4f}")
    
    # Save best model
    print("\nSaving best model...")
    os.makedirs('data/model', exist_ok=True)
    
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'features': list(X.columns),
        'model_name': best_name
    }
    
    with open('data/model/rf_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"Model saved to: data/model/rf_model.pkl")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"\nBest Model: {best_name}")
    print(f"Accuracy: {best_accuracy*100:.2f}%")
    print("\nImprovements from base model:")
    print("  - Added recent form features (last 5 games)")
    print("  - Class balancing to handle draws better")
    print("  - Tested multiple algorithms")
    print("\nThe improved model is ready for predictions!\n")


if __name__ == "__main__":
    train_multiple_models()