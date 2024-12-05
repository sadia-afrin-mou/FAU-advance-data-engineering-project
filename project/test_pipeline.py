import warnings
import urllib3
import pytest
import pandas as pd
import sqlite3
from pathlib import Path
import os

# Filter warnings more specifically
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="kaggle.*")
warnings.filterwarnings("ignore", message=".*getheaders.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=pytest.PytestUnknownMarkWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

from pipeline import (
    setup_kaggle_credentials,
    download_dataset,
    download_emissions_data,
    process_emissions_data,
    preprocess_renewable_energy,
    preprocess_pollution,
    main
)



@pytest.fixture
def sample_emissions_df():
    """Create a sample emissions DataFrame for testing"""
    return pd.DataFrame({
        'State FIPS': ['01', '02'],
        'State': ['AL', 'AK'], 
        'Tier 1 Code': ['01', '02'],
        'Tier 1 Description': ['Fuel Comb. Elec. Util.', 'Fuel Comb. Industrial'],
        'Pollutant': ['Black Carbon', 'CO'],
        'emissions1990': [1.0891923295, 2.0891923295],
        'emissions1996': [1.1891923295, 2.1891923295], 
        'emissions1997': [1.2891923295, 2.2891923295],
        'emissions1998': [1.3891923295, 2.3891923295],
        'emissions1999': [1.4891923295, 2.4891923295],
        'emissions2000': [1.5891923295, 2.5891923295],
        'emissions2001': [1.6891923295, 2.6891923295],
        'emissions2002': [1.7891923295, 2.7891923295],
        'emissions2003': [1.8891923295, 2.8891923295],
        'emissions2004': [1.9891923295, 2.9891923295],
        'emissions2005': [2.0891923295, 3.0891923295],
        'emissions2006': [2.1891923295, 3.1891923295],
        'emissions2007': [2.2891923295, 3.2891923295],
        'emissions2008': [2.3891923295, 3.3891923295],
        'emissions2009': [2.4891923295, 3.4891923295],
        'emissions2010': [2.5891923295, 3.5891923295],
        'emissions2011': [2.6891923295, 3.6891923295],
        'emissions2012': [2.7891923295, 3.7891923295],
        'emissions2013': [2.8891923295, 3.8891923295],
        'emissions2014': [2.9891923295, 3.9891923295],
        'emissions2015': [3.0891923295, 4.0891923295],
        'emissions2016': [3.1891923295, 4.1891923295],
        'emissions2017': [3.2891923295, 4.2891923295],
        'emissions2018': [3.3891923295, 4.3891923295],
        'emissions2019': [3.4891923295, 4.4891923295],
        'emissions2020': [3.5891923295, 4.5891923295],
        'emissions2021': [3.6891923295, 4.6891923295],
        'emissions2022': [3.7891923295, 4.7891923295],
        'emissions2023': [3.8891923295, 4.8891923295]
    })

@pytest.fixture
def sample_renewable_df():
    """Create a sample renewable energy DataFrame for testing"""
    return pd.DataFrame({
        'Year': [1973, 1973, 1973],
        'Month': [1, 1, 1],
        'Sector': ['Commerical', 'Electric Power', 'Industrial'],
        'Hydroelectric Power': [0, 0, 1.04],
        'Geothermal Energy': [0, 0.49, 0],
        'Solar Energy': [0, 0, 0],
        'Wind Energy': [0, 0, 0],
        'Wood Energy': [0.57, 0.054, 98.933],
        'Waste Energy': [0, 0.157, 0],
        'Fuel Ethanol, Excluding Denaturant': [0, 0, 0],
        'Biomass Losses and Co-products': [0, 0, 0],
        'Biomass Energy': [0.57, 0.211, 98.933],
        'Total Renewable Energy': [0.57, 89.223, 99.973],
        'Renewable Diesel Fuel': [0, 0, 0],
        'Other Biofuels': [0, 0, 0],
        'Conventional Hydroelectric Power': [0, 88.522, 0],
        'Biodiesel': [0, 0, 0]
    })

@pytest.fixture
def sample_pollution_df():
    """Create a sample pollution DataFrame for testing"""
    return pd.DataFrame({
        'Date': ['2000-01-01', '2000-01-02'],
        'Address': ['1645 E ROOSEVELT ST-CENTRAL PHOENIX STN', '1645 E ROOSEVELT ST-CENTRAL PHOENIX STN'],
        'State': ['Arizona', 'Arizona'],
        'County': ['Maricopa', 'Maricopa'],
        'City': ['Phoenix', 'Phoenix'],
        'O3 Mean': [0.019765, 0.015882],
        'O3 1st Max Value': [0.04, 0.032],
        'O3 1st Max Hour': [10, 10],
        'O3 AQI': [37, 30],
        'CO Mean': [0.878947, 1.066667],
        'CO 1st Max Value': [2.2, 2.3],
        'CO 1st Max Hour': [23, 0],
        'CO AQI': [25.0, 26.0],
        'SO2 Mean': [3.0, 1.958333],
        'SO2 1st Max Value': [9.0, 3.0],
        'SO2 1st Max Hour': [21, 22],
        'SO2 AQI': [13.0, 4.0],
        'NO2 Mean': [19.041667, 22.958333],
        'NO2 1st Max Value': [49.0, 36.0],
        'NO2 1st Max Hour': [19, 19],
        'NO2 AQI': [46, 34],
        'Unnamed: 0': [0, 1]
    })

def test_process_emissions_data(sample_emissions_df):
    """Test emissions data processing"""
    processed_df = process_emissions_data(sample_emissions_df)
    
    assert 'State' in processed_df.columns
    assert 'Year' in processed_df.columns
    assert 'Emissions' in processed_df.columns
    assert len(processed_df) == 58
    assert 'Alabama' in processed_df['State'].values
    assert 'Alaska' in processed_df['State'].values

def test_preprocess_renewable_energy(sample_renewable_df):
    """Test renewable energy data preprocessing"""
    processed_df = preprocess_renewable_energy(sample_renewable_df)
    
    assert not processed_df.isnull().any().any()
    assert len(processed_df) == len(sample_renewable_df)

def test_preprocess_pollution(sample_pollution_df):
    """Test pollution data preprocessing"""
    processed_df = preprocess_pollution(sample_pollution_df)
    
    assert 'Year' in processed_df.columns
    assert 'Month' in processed_df.columns
    assert 'Day' in processed_df.columns
    assert 'Unnamed: 0' not in processed_df.columns
    assert processed_df['State'].str.contains(r'\s+$').sum() == 0  # No trailing spaces
    assert not processed_df.isnull().any().any()

@pytest.mark.integration
def test_full_pipeline():
    """System-level test for the complete pipeline"""
    # Setup: Clean any existing test data
    db_path = Path('data/data.db')
    if db_path.exists():
        db_path.unlink()
    
    # Execute the pipeline
    main()
    
    # Verify database exists and contains expected tables
    assert db_path.exists(), "Database file was not created"
    
    # Connect to database and verify tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {'renewable_energy', 'pollution', 'emissions'}
    assert expected_tables.issubset(tables), "Not all expected tables were created"
    
    # Verify each table has data
    for table in expected_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        assert count > 0, f"Table {table} is empty"
    
    # Verify all expected columns exist in each table
    expected_columns = {
        'renewable_energy': {
            'Hydroelectric Power', 'Waste Energy', 'Geothermal Energy', 'Wind Energy',
            'Biomass Losses and Co-products', 'Fuel Ethanol, Excluding Denaturant',
            'Total Renewable Energy', 'Biodiesel', 'Sector', 'Month', 'Wood Energy',
            'Biomass Energy', 'Solar Energy', 'Conventional Hydroelectric Power',
            'Other Biofuels', 'Year', 'Renewable Diesel Fuel'
        },
        'pollution': {
            'O3 AQI', 'O3 Mean', 'City', 'O3 1st Max Hour', 'Day', 'NO2 Mean',
            'County', 'Year', 'CO Mean', 'CO 1st Max Value', 'CO AQI', 'NO2 AQI',
            'NO2 1st Max Hour', 'Date', 'Address', 'CO 1st Max Hour',
            'NO2 1st Max Value', 'SO2 AQI', 'SO2 1st Max Hour', 'O3 1st Max Value',
            'State', 'SO2 Mean', 'Month', 'SO2 1st Max Value'
        },
        'emissions': {
            'State', 'Emissions', 'Pollutant', 'Year', 'Source'
        }
    }

    for table, expected_cols in expected_columns.items():
        cursor.execute(f"PRAGMA table_info({table})")
        actual_cols = {row[1] for row in cursor.fetchall()}  # row[1] contains column name
        assert expected_cols.issubset(actual_cols), f"Missing columns in {table} table. Expected {expected_cols - actual_cols}"
    
    # Verify column types for each table
    expected_types = {
        'renewable_energy': {
            'Year': 'INTEGER', 'Month': 'INTEGER', 'Sector': 'TEXT',
            'Hydroelectric Power': 'REAL', 'Geothermal Energy': 'REAL',
            'Solar Energy': 'REAL', 'Wind Energy': 'REAL', 'Wood Energy': 'REAL',
            'Waste Energy': 'REAL', 'Fuel Ethanol, Excluding Denaturant': 'REAL',
            'Biomass Losses and Co-products': 'REAL', 'Biomass Energy': 'REAL',
            'Total Renewable Energy': 'REAL', 'Renewable Diesel Fuel': 'REAL',
            'Other Biofuels': 'REAL', 'Conventional Hydroelectric Power': 'REAL',
            'Biodiesel': 'REAL'
        },
        'pollution': {
            'Date': 'TIMESTAMP', 'Address': 'TEXT', 'State': 'TEXT',
            'County': 'TEXT', 'City': 'TEXT', 'O3 Mean': 'REAL',
            'O3 1st Max Value': 'REAL', 'O3 1st Max Hour': 'INTEGER',
            'O3 AQI': 'INTEGER', 'CO Mean': 'REAL', 'CO 1st Max Value': 'REAL',
            'CO 1st Max Hour': 'INTEGER', 'CO AQI': 'REAL', 'SO2 Mean': 'REAL',
            'SO2 1st Max Value': 'REAL', 'SO2 1st Max Hour': 'INTEGER',
            'SO2 AQI': 'REAL', 'NO2 Mean': 'REAL', 'NO2 1st Max Value': 'REAL',
            'NO2 1st Max Hour': 'INTEGER', 'NO2 AQI': 'INTEGER',
            'Year': 'INTEGER', 'Month': 'INTEGER', 'Day': 'INTEGER'
        },
        'emissions': {
            'Year': 'INTEGER', 'State': 'TEXT', 'Source': 'TEXT',
            'Pollutant': 'TEXT', 'Emissions': 'REAL'
        }
    }

    for table, type_dict in expected_types.items():
        cursor.execute(f"PRAGMA table_info({table})")
        actual_types = {row[1]: row[2] for row in cursor.fetchall()}  # row[1] is name, row[2] is type
        
        for column, expected_type in type_dict.items():
            assert column in actual_types, f"Column {column} not found in {table}"
            actual_type = actual_types[column].upper()
            assert actual_type == expected_type, f"Wrong type for {table}.{column}: expected {expected_type}, got {actual_type}"
    conn.close()
    
    # Clean up
    db_path.unlink()