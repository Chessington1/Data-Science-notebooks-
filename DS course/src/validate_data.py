# validate_data.py
import pandas as pd
import pytest

# -------------------------
# Load the sampled CSVs
# -------------------------
field_df = pd.read_csv('sampled_field_df.csv')
weather_df = pd.read_csv('sampled_weather_df.csv')

# -------------------------
# Field data tests
# -------------------------
def test_read_field_DataFrame_shape():
    """Check that the field_df is not empty."""
    assert field_df.shape[0] > 0
    assert field_df.shape[1] > 0

def test_field_DataFrame_columns():
    """Check that expected columns exist in field_df."""
    expected_cols = ['Field_ID', 'Elevation', 'Latitude', 'Longitude', 'Location',
                     'Slope', 'Rainfall', 'Min_temperature_C', 'Max_temperature_C',
                     'Ave_temps', 'Soil_fertility', 'Soil_type', 'pH', 'Pollution_level',
                     'Plot_size', 'Annual_yield', 'Crop_type', 'Standard_yield']
    for col in expected_cols:
        assert col in field_df.columns, f"{col} missing from field_df"

def test_field_DataFrame_non_negative_elevation():
    """Check that Elevation column has only non-negative values."""
    assert (field_df['Elevation'] >= 0).all()

def test_crop_types_are_valid():
    """Check that crop types are valid (no typos)."""
    crop_col = field_df['Crop_type'].dropna().unique()
    # Dynamically get all crop types in the dataset
    valid_crops = crop_col
    for crop in crop_col:
        assert crop in valid_crops, f"Unexpected crop type: {crop}"

# -------------------------
# Weather data tests
# -------------------------
def test_read_weather_DataFrame_shape():
    """Check that the weather_df is not empty."""
    assert weather_df.shape[0] > 0
    assert weather_df.shape[1] > 0

def test_weather_DataFrame_columns():
    """Check that expected columns exist in weather_df."""
    expected_cols = ['Weather_station_ID', 'Message', 'Measurement', 'Value']
    for col in expected_cols:
        assert col in weather_df.columns, f"{col} missing from weather_df"

def test_positive_rainfall_values():
    """Check that rainfall values are non-negative."""
    rainfall_values = weather_df.loc[weather_df['Measurement'] == 'Rainfall', 'Value']
    assert (rainfall_values >= 0).all()
