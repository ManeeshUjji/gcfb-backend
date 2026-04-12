"""
Model Inference Utilities for Demand Forecasting.

This module provides functions to load the trained model and make predictions
for the API endpoints.
"""

import os
import pickle
from typing import Dict, List, Optional
import pandas as pd
from datetime import date


_MODEL_CACHE = None


def load_model():
    """
    Load the trained model from pickle file.
    Uses caching to avoid repeated file I/O.
    
    Returns:
        Model package dict containing model and metadata
    """
    global _MODEL_CACHE
    
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    
    model_path = os.path.join(os.path.dirname(__file__), 'demand_model.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Please run train_model.py first."
        )
    
    with open(model_path, 'rb') as f:
        _MODEL_CACHE = pickle.load(f)
    
    return _MODEL_CACHE


def predict_headcount(
    zip_code: str,
    program_type: str,
    prediction_date: date,
    temperature_f: float,
    precipitation_inches: float,
    poverty_rate: float,
    capacity_per_day: int
) -> Dict:
    """
    Predict headcount for a given site and date.
    
    Args:
        zip_code: ZIP code of the site
        program_type: Type of program (pantry, senior, kids_cafe, mobile, shelter)
        prediction_date: Date for prediction
        temperature_f: Forecasted temperature in Fahrenheit
        precipitation_inches: Forecasted precipitation in inches
        poverty_rate: Poverty rate for the ZIP code
        capacity_per_day: Daily capacity of the site
    
    Returns:
        Dict with prediction and confidence interval
    """
    model_pkg = load_model()
    model = model_pkg['model']
    zip_encoder = model_pkg['zip_encoder']
    program_encoder = model_pkg['program_encoder']
    feature_columns = model_pkg['feature_columns']
    
    # Extract temporal features
    day_of_week = prediction_date.weekday()
    day_of_month = prediction_date.day
    month = prediction_date.month
    
    # Encode categorical variables
    # Handle unknown ZIP codes gracefully
    try:
        zip_code_encoded = zip_encoder.transform([zip_code])[0]
    except ValueError:
        # Use the most common ZIP code if unknown
        zip_code_encoded = 0
    
    # Handle unknown program types gracefully
    try:
        program_type_encoded = program_encoder.transform([program_type])[0]
    except ValueError:
        # Use the most common program type if unknown
        program_type_encoded = 0
    
    # Create feature vector
    features = pd.DataFrame({
        'day_of_week': [day_of_week],
        'day_of_month': [day_of_month],
        'month': [month],
        'zip_code_encoded': [zip_code_encoded],
        'program_type_encoded': [program_type_encoded],
        'temperature_f': [temperature_f],
        'precipitation_inches': [precipitation_inches],
        'poverty_rate': [poverty_rate],
        'capacity_per_day': [capacity_per_day]
    })
    
    # Ensure column order matches training
    features = features[feature_columns]
    
    # Make prediction
    prediction = model.predict(features)[0]
    
    # Calculate confidence interval using model's estimators
    # Get predictions from all trees
    tree_predictions = [tree.predict(features)[0] for tree in model.estimators_]
    std_dev = pd.Series(tree_predictions).std()
    
    # 95% confidence interval (±2 standard deviations)
    lower_bound = max(20, int(prediction - 2 * std_dev))
    upper_bound = min(800, int(prediction + 2 * std_dev))
    
    return {
        'predicted_headcount': int(prediction),
        'confidence_interval': {
            'lower': lower_bound,
            'upper': upper_bound
        },
        'std_dev': float(std_dev)
    }


def batch_predict(
    sites_data: List[Dict],
    prediction_date: date,
    weather_by_zip: Dict[str, Dict]
) -> List[Dict]:
    """
    Make predictions for multiple sites at once.
    
    Args:
        sites_data: List of site dictionaries with ZIP, program_type, etc.
        prediction_date: Date for prediction
        weather_by_zip: Dict mapping ZIP code to weather forecast
    
    Returns:
        List of predictions with site information
    """
    model_pkg = load_model()
    
    predictions = []
    
    for site in sites_data:
        weather = weather_by_zip.get(site['zip_code'], {
            'temperature_f': 60.0,
            'precipitation_inches': 0.0
        })
        
        pred = predict_headcount(
            zip_code=site['zip_code'],
            program_type=site['program_type'],
            prediction_date=prediction_date,
            temperature_f=weather['temperature_f'],
            precipitation_inches=weather['precipitation_inches'],
            poverty_rate=site.get('poverty_rate', 0.15),
            capacity_per_day=site['capacity_per_day']
        )
        
        predictions.append({
            'site_id': site.get('site_id'),
            'zip_code': site['zip_code'],
            'program_type': site['program_type'],
            **pred
        })
    
    return predictions


def get_feature_importances() -> List[Dict]:
    """
    Get feature importances from the trained model.
    
    Returns:
        List of feature importance dictionaries
    """
    model_pkg = load_model()
    return model_pkg['feature_importances']


def get_top_factors(
    zip_code: str,
    prediction_date: date,
    poverty_rate: float,
    n: int = 3
) -> List[Dict]:
    """
    Get top N contributing factors for a prediction.
    
    Args:
        zip_code: ZIP code
        prediction_date: Date of prediction
        poverty_rate: Poverty rate for the ZIP
        n: Number of top factors to return
    
    Returns:
        List of top contributing factors with explanations
    """
    importances = get_feature_importances()
    
    # Get top N features by importance
    top_features = sorted(importances, key=lambda x: x['importance'], reverse=True)[:n]
    
    # Create human-readable explanations
    factors = []
    
    for feat in top_features:
        feature_name = feat['feature']
        importance = feat['importance']
        
        explanation = _get_feature_explanation(
            feature_name, prediction_date, poverty_rate, importance
        )
        
        factors.append({
            'feature': feature_name,
            'importance': importance,
            'explanation': explanation
        })
    
    return factors


def _get_feature_explanation(
    feature_name: str,
    prediction_date: date,
    poverty_rate: float,
    importance: float
) -> str:
    """Generate human-readable explanation for a feature."""
    
    explanations = {
        'poverty_rate': f"High poverty rate ({poverty_rate:.1%}) increases demand",
        'day_of_month': f"Day {prediction_date.day} of month (SNAP timing pattern)",
        'month': f"Month {prediction_date.strftime('%B')} (seasonal pattern)",
        'day_of_week': f"{prediction_date.strftime('%A')} demand pattern",
        'temperature_f': "Weather conditions affect turnout",
        'precipitation_inches': "Precipitation impacts attendance",
        'capacity_per_day': "Site capacity influences demand",
        'zip_code_encoded': "Geographic location factor",
        'program_type_encoded': "Program type characteristic"
    }
    
    return explanations.get(feature_name, f"{feature_name} contributes to prediction")


def get_model_metrics() -> Dict:
    """
    Get model performance metrics.
    
    Returns:
        Dict with training metrics
    """
    model_pkg = load_model()
    return model_pkg.get('metrics', {})


def invalidate_cache():
    """Clear the model cache (useful for testing or model updates)."""
    global _MODEL_CACHE
    _MODEL_CACHE = None
