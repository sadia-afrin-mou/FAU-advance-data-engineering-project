import os
import kaggle
import pandas as pd
import sqlite3
from pathlib import Path

def setup_kaggle_credentials():
    """Ensure Kaggle API credentials are set up"""
    if not os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')):
        raise Exception("Please place your kaggle.json in ~/.kaggle/ directory")
    # Set permissions for kaggle.json
    # os.chmod(os.path.expanduser('~/.kaggle/kaggle.json'), 600)

def download_dataset(dataset_name, path):
    """Download dataset from Kaggle"""
    kaggle.api.dataset_download_files(dataset_name, path=path, unzip=True)

def create_database():
    """Create SQLite database and necessary tables"""
    db_path = Path('data/data.db')
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS renewable_energy (
    #         Year INTEGER,
    #         Month INTEGER,
    #         Sector TEXT,
    #         Hydroelectric_Power REAL,
    #         Geothermal_Energy REAL,
    #         Solar_Energy REAL,
    #         Wind_Energy REAL,
    #         Wood_Energy REAL,
    #         Waste_Energy REAL,
    #         Fuel_Ethanol_Excluding_Denaturant REAL,
    #         Biomass_Losses_and_Coproducts REAL,
    #         Biomass_Energy REAL,
    #         Total_Renewable_Energy REAL,
    #         Renewable_Diesel_Fuel REAL,
    #         Other_Biofuels REAL,
    #         Conventional_Hydroelectric_Power REAL,
    #         Biodiesel REAL
    #     )
    # ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS pollution (
    #         Year INTEGER,
    #         Month INTEGER,
    #         Day INTEGER,
    #         date DATE,
    #         state VARCHAR(50),
    #         o3_mean FLOAT,
    #         o3_max_value FLOAT,
    #         o3_max_hour INTEGER,
    #         o3_aqi FLOAT,
    #         co_mean FLOAT,
    #         co_max_value FLOAT,
    #         co_max_hour INTEGER,
    #         co_aqi FLOAT,
    #         so2_mean FLOAT,
    #         so2_max_value FLOAT,
    #         so2_max_hour INTEGER,
    #         so2_aqi FLOAT,
    #         no2_mean FLOAT,
    #         no2_max_value FLOAT,
    #         no2_max_hour INTEGER,
    #         no2_aqi FLOAT,
    #         pollution_index FLOAT
    #     )
    # ''')

    conn.commit()
    return conn

def preprocess_renewable_energy(df):
    """Preprocess renewable energy dataset"""
    # Basic data validation
    assert not df.empty, "Renewable energy dataset is empty"
    assert df.duplicated().sum() == 0, "Found duplicates in renewable energy data"
    
    # Return the original dataframe as we want to keep the raw structure
    return df

def preprocess_pollution(df):
    """Preprocess pollution dataset"""
    # Basic data validation
    assert not df.empty, "Pollution dataset is empty"
    assert df.duplicated().sum() == 0, "Found duplicates in pollution data"
    
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df.drop(columns=['Unnamed: 0', 'City', 'County', 'Address'], inplace=True)
    # Strip whitespace from 'State' column
    df['State'] = df['State'].apply(lambda x: x.strip())
    # Extract year, month, and day from Date to make it compatible with renewable energy dataset and to analyze seasonality.
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    # Return the original dataframe as we want to keep the raw structure
    return df

def main():
    # Setup
    setup_kaggle_credentials()
    temp_dir = Path('data/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Download datasets from Kaggle
    datasets = {
        'alistairking/renewable-energy-consumption-in-the-u-s': 'dataset.csv',
        'guslovesmath/us-pollution-data-200-to-2022': 'pollution_2000_2023.csv'
    }

    # Only download if files don't exist
    for dataset_name, filename in datasets.items():
        file_path = temp_dir / filename
        # if not file_path.exists():
        download_dataset(dataset_name, temp_dir)

    # Download and process datasets
    renewable_df = preprocess_renewable_energy(pd.read_csv(temp_dir / 'dataset.csv'))
    pollution_df = preprocess_pollution(pd.read_csv(temp_dir / 'pollution_2000_2023.csv'))

    # Create database connection
    conn = create_database()
    
    renewable_df.to_sql('renewable_energy', conn, if_exists='replace', index=False)
    pollution_df.to_sql('pollution', conn, if_exists='replace', index=False)
    
    conn.close()
    for file in temp_dir.glob('*'):
        file.unlink()
    temp_dir.rmdir()

if __name__ == "__main__":
    main()
