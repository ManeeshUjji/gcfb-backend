# Models Directory

This directory contains the machine learning models for demand forecasting.

## Files

- `demand_model.pkl` - Serialized Random Forest model (generated during Milestone 2)
- Model will be trained on 90-day historical data with features:
  - ZIP code (encoded)
  - Day of week (0-6)
  - Day of month (1-31)
  - Program type (encoded)
  - Temperature forecast (°F)
  - Precipitation forecast (inches)
  - Census poverty rate

## Usage

The model is loaded at application startup and used for forecast inference via the `/forecast` endpoints.

See `spec.md` for complete model specification.
