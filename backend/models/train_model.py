"""
Machine Learning Model Training Script for Demand Forecasting.

This script trains a Random Forest Regressor on historical distribution data
with engineered features to predict headcount demand at partner sites.
"""

import sys
import os
import pickle
from datetime import datetime, date
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

sys.path.append('..')
from db import get_engine, get_session, HistoricalDistribution, PartnerSite
from data.zip_coordinates import get_all_zips


def load_training_data(session):
    """
    Load historical distribution data with joined partner site information.
    
    Returns:
        DataFrame with all necessary features for training
    """
    print("Loading historical distribution data...")
    
    # Query all historical data with partner site info
    query = session.query(
        HistoricalDistribution.date,
        HistoricalDistribution.headcount,
        HistoricalDistribution.temperature_f,
        HistoricalDistribution.precipitation_inches,
        PartnerSite.zip_code,
        PartnerSite.program_type,
        PartnerSite.capacity_per_day
    ).join(
        PartnerSite,
        HistoricalDistribution.site_id == PartnerSite.id
    )
    
    results = query.all()
    
    df = pd.DataFrame(results, columns=[
        'date', 'headcount', 'temperature_f', 'precipitation_inches',
        'zip_code', 'program_type', 'capacity_per_day'
    ])
    
    print(f"Loaded {len(df)} historical records")
    return df


def engineer_features(df):
    """
    Engineer features from raw data.
    
    Features:
    - day_of_week (0-6)
    - day_of_month (1-31)
    - month (1-12)
    - zip_code (encoded)
    - program_type (encoded)
    - temperature_f
    - precipitation_inches
    - poverty_rate (from ZIP data)
    - capacity_per_day
    """
    print("Engineering features...")
    
    # Temporal features
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
    df['day_of_month'] = pd.to_datetime(df['date']).dt.day
    df['month'] = pd.to_datetime(df['date']).dt.month
    
    # Load poverty data by ZIP
    zip_data = {z['zip']: z['poverty_rate'] for z in get_all_zips()}
    df['poverty_rate'] = df['zip_code'].map(zip_data)
    
    # Fill any missing poverty rates with median
    median_poverty = df['poverty_rate'].median()
    df['poverty_rate'] = df['poverty_rate'].fillna(median_poverty)
    
    # Encode categorical variables
    zip_encoder = LabelEncoder()
    program_encoder = LabelEncoder()
    
    df['zip_code_encoded'] = zip_encoder.fit_transform(df['zip_code'])
    df['program_type_encoded'] = program_encoder.fit_transform(df['program_type'])
    
    # Select features for training
    feature_columns = [
        'day_of_week', 'day_of_month', 'month',
        'zip_code_encoded', 'program_type_encoded',
        'temperature_f', 'precipitation_inches',
        'poverty_rate', 'capacity_per_day'
    ]
    
    X = df[feature_columns]
    y = df['headcount']
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    
    return X, y, zip_encoder, program_encoder, feature_columns


def train_model(X, y):
    """
    Train Random Forest Regressor model.
    
    Returns:
        Trained model and performance metrics
    """
    print("\nSplitting data into train/test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    print("\nTraining Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("Model training complete!")
    
    # Evaluate on test set
    print("\nEvaluating model performance...")
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"R² Score: {r2:.4f}")
    
    metrics = {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'trained_at': datetime.now().isoformat()
    }
    
    return model, metrics


def extract_feature_importances(model, feature_columns):
    """
    Extract and rank feature importances.
    
    Returns:
        DataFrame with features ranked by importance
    """
    print("\nExtracting feature importances...")
    
    importances = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 5 Most Important Features:")
    for idx, row in importances.head(5).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    return importances


def serialize_model(model, zip_encoder, program_encoder, feature_columns, importances, metrics):
    """
    Serialize model and metadata to pickle file.
    """
    print("\nSerializing model to demand_model.pkl...")
    
    model_package = {
        'model': model,
        'zip_encoder': zip_encoder,
        'program_encoder': program_encoder,
        'feature_columns': feature_columns,
        'feature_importances': importances.to_dict('records'),
        'metrics': metrics,
        'version': '1.0.0',
        'trained_at': datetime.now().isoformat()
    }
    
    model_path = os.path.join(os.path.dirname(__file__), 'demand_model.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_package, f)
    
    print(f"Model saved to: {model_path}")
    print(f"Model size: {os.path.getsize(model_path) / 1024:.2f} KB")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("GCFB Demand Forecasting Model Training")
    print("=" * 60)
    print()
    
    # Load environment and create session
    from dotenv import load_dotenv
    load_dotenv()
    
    engine = get_engine()
    session = get_session(engine)
    
    try:
        # Step 1: Load data
        df = load_training_data(session)
        
        # Step 2: Engineer features
        X, y, zip_encoder, program_encoder, feature_columns = engineer_features(df)
        
        # Step 3: Train model
        model, metrics = train_model(X, y)
        
        # Step 4: Extract feature importances
        importances = extract_feature_importances(model, feature_columns)
        
        # Step 5: Serialize model
        serialize_model(model, zip_encoder, program_encoder, feature_columns, importances, metrics)
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print("\nModel is ready for inference via the API.")
        print("Use model_utils.py for loading and prediction.")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
