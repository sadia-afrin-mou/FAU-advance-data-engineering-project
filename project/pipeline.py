import os
import kaggle
import pandas as pd
import sqlite3
from pathlib import Path
import requests
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_kaggle_credentials():
    """Ensure Kaggle API credentials are set up"""
    logger.info("Setting up Kaggle credentials...")
    if not os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')):
        logger.error("Kaggle credentials not found")
        raise Exception("Please place your kaggle.json in ~/.kaggle/ directory")
    logger.info("Kaggle credentials verified successfully")
    # Set permissions for kaggle.json
    # os.chmod(os.path.expanduser('~/.kaggle/kaggle.json'), 600)

def download_dataset(dataset_name, path):
    """Download dataset from Kaggle"""
    logger.info(f"Downloading dataset {dataset_name} to {path}")
    kaggle.api.dataset_download_files(dataset_name, path=path, unzip=True)
    logger.info(f"Successfully downloaded and unzipped {dataset_name}")

def download_emissions_data():
    """Download and process emissions data from EPA website"""
    url = "https://www.epa.gov/system/files/other-files/2024-02/state_tier1_08feb2024_ktons.xlsx"
    logger.info(f"Downloading emissions data from {url}")
    response = requests.get(url)

    # Check if download was successful
    if response.status_code == 200:
        logger.info("Successfully downloaded emissions data")
        # Read Excel file into pandas DataFrame
        excel_data = BytesIO(response.content)
        df_emissions = pd.read_excel(excel_data, sheet_name='State_Trends', skiprows=1)
        logger.info(f"Loaded emissions data: {len(df_emissions)} rows")
        return df_emissions
    else:
        logger.error(f"Failed to download emissions data. Status code: {response.status_code}")
        return None
    
def create_database():
    """Create SQLite database and necessary tables"""
    db_path = Path('data/data.db')
    logger.info(f"Creating database at {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    logger.info("Database connection established")

    conn.commit()
    return conn

def preprocess_renewable_energy(df):
    """Preprocess renewable energy dataset"""
    logger.info("Starting renewable energy data preprocessing")
    # Basic data validation
    assert not df.empty, "Renewable energy dataset is empty"
    logger.info(f"Initial renewable energy dataset size: {len(df)} rows")
    
    # Handle duplicates
    if df.duplicated().sum() > 0:
        dups = df.duplicated().sum()
        logger.info(f"Found {dups} duplicates in renewable energy data. Removing duplicates...")
        df = df.drop_duplicates()
        logger.info(f"After removing duplicates: {len(df)} rows")
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        logger.info("Found missing values. Filling with forward fill method...")
        df = df.fillna(method='ffill')
        # For any remaining NaN at the start, fill with backward fill
        df = df.fillna(method='bfill')
        logger.info("Missing values handled successfully")
    
    logger.info("Renewable energy preprocessing completed")
    return df

def preprocess_pollution(df):
    """Preprocess pollution dataset"""
    logger.info("Starting pollution data preprocessing")
    # Basic data validation
    assert not df.empty, "Pollution dataset is empty"
    logger.info(f"Initial pollution dataset size: {len(df)} rows")

    if df.duplicated().sum() > 0:
        dups = df.duplicated().sum()
        logger.info(f"Found {dups} duplicates in pollution data. Removing duplicates...")
        df = df.drop_duplicates()
        logger.info(f"After removing duplicates: {len(df)} rows")
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        logger.info("Found missing values. Filling with forward fill method...")
        df = df.fillna(method='ffill')
        # For any remaining NaN at the start, fill with backward fill
        df = df.fillna(method='bfill')
        logger.info("Missing values handled successfully")
    
    logger.info("Converting Date column to datetime")
    df['Date'] = pd.to_datetime(df['Date'])
    df.drop(columns=['Unnamed: 0'], inplace=True)
    logger.info("Dropped Unnamed: 0 column")
    
    # Strip whitespace from 'State' column
    df['State'] = df['State'].apply(lambda x: x.strip())
    # Extract year, month, and day from Date
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    logger.info("Added Year, Month, Day columns")
    
    logger.info("Pollution preprocessing completed")
    return df

def process_emissions_data(df_emissions):
    """
    Process emissions data by cleaning column names, reshaping data, and standardizing format
    """
    logger.info("Starting emissions data processing")
    
    if not isinstance(df_emissions, pd.DataFrame):
        logger.error("Input is not a pandas DataFrame")
        raise TypeError("Input must be a pandas DataFrame")
        
    required_cols = ['State FIPS', 'State', 'Tier 1 Code', 'Tier 1 Description', 'Pollutant']
    missing_cols = [col for col in required_cols if col not in df_emissions.columns]
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        raise ValueError(f"Missing required columns: {missing_cols}")

    try:
        logger.info("Cleaning column names")
        emissions_cols = [col for col in df_emissions.columns if col.startswith('emissions')]
        rename_dict = {col: col.replace('emissions', '') for col in emissions_cols}
        df_emissions = df_emissions.rename(columns=rename_dict)

        logger.info("Reshaping data")
        year_columns = [col for col in df_emissions.columns if col.isdigit()]
        if not year_columns:
            logger.error("No year columns found in the data")
            raise ValueError("No year columns found in the data")
            
        df_emissions = df_emissions.melt(
            id_vars=['State FIPS', 'State', 'Tier 1 Code', 'Tier 1 Description', 'Pollutant'],
            value_vars=year_columns,
            var_name='Year',
            value_name='Emissions'
        )
        logger.info(f"Data reshaped successfully. New shape: {df_emissions.shape}")

        logger.info("Converting and cleaning data")
        df_emissions['Year'] = df_emissions['Year'].astype(int)
        df_emissions = df_emissions.sort_values(['State', 'Pollutant', 'Year'])
        df_emissions['Emissions'] = df_emissions['Emissions'].fillna(0)
        
        logger.info("Dropping unnecessary columns and renaming")
        df_emissions = df_emissions.drop(columns=['State FIPS', 'Tier 1 Code'])
        df_emissions = df_emissions.rename(columns={'Tier 1 Description': 'Source'})
        df_emissions = df_emissions.reset_index(drop=True)
        
        # Dictionary mapping state abbreviations to full names
        abbreviation_to_name = {
            "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona",
            "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
            "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "IA": "Iowa",
            "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas",
            "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland",
            "ME": "Maine", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri",
            "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina", "ND": "North Dakota",
            "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
            "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma",
            "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
            "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
            "VA": "Virginia", "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin",
            "WV": "West Virginia", "WY": "Wyoming", "DC": "District of Columbia",
            "AS": "American Samoa", "GU": "Guam GU", "MP": "Northern Mariana Islands",
            "PR": "Puerto Rico PR", "VI": "U.S. Virgin Islands"
        }
        
        logger.info("Replacing state abbreviations with full names")
        df_emissions['State'] = df_emissions['State'].map(abbreviation_to_name)
        df_emissions = df_emissions[['Year', 'State', 'Source', 'Pollutant', 'Emissions']]
        logger.info("Emissions data processing completed successfully")
        return df_emissions

    except Exception as e:
        logger.error(f"Error processing emissions data: {str(e)}")
        raise RuntimeError(f"Error processing emissions data: {str(e)}")
    
def main():
    logger.info("Starting pipeline execution")
    # Setup
    setup_kaggle_credentials()
    temp_dir = Path('data/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created temporary directory at {temp_dir}")

    # Download datasets from Kaggle
    datasets = {
        'alistairking/renewable-energy-consumption-in-the-u-s': 'dataset.csv',
        'guslovesmath/us-pollution-data-200-to-2022': 'pollution_2000_2023.csv'
    }

    # Only download if files don't exist
    max_retries = 3
    for dataset_name, filename in datasets.items():
        file_path = temp_dir / filename
        retry_count = 0
        while retry_count < max_retries:
            try:
                download_dataset(dataset_name, temp_dir)
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"Failed to download {dataset_name} after {max_retries} attempts")
                    raise RuntimeError(f"Failed to download {dataset_name}: {str(e)}")
                logger.warning(f"Attempt {retry_count} failed, retrying download of {dataset_name}...")
        
    # Download and process emissions data with retries
    logger.info("Downloading and processing emissions data")
    retry_count = 0
    while retry_count < max_retries:
        try:
            emissions_df = download_emissions_data()
            if emissions_df is not None:
                emissions_df = process_emissions_data(emissions_df)
                break
            retry_count += 1
            if retry_count == max_retries:
                logger.error("Failed to download emissions data after all retries")
                raise RuntimeError("Failed to download emissions data")
            logger.warning(f"Attempt {retry_count} failed, retrying emissions data download...")
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Failed to process emissions data after {max_retries} attempts")
                raise RuntimeError(f"Failed to process emissions data: {str(e)}")
            logger.warning(f"Attempt {retry_count} failed, retrying emissions data processing...")
        
    # Download and process datasets
    logger.info("Processing renewable energy and pollution datasets")
    renewable_df = preprocess_renewable_energy(pd.read_csv(temp_dir / 'dataset.csv'))
    pollution_df = preprocess_pollution(pd.read_csv(temp_dir / 'pollution_2000_2023.csv'))

    # Create database connection
    logger.info("Creating database and saving data")
    conn = create_database()
    
    renewable_df.to_sql('renewable_energy', conn, if_exists='replace', index=False)
    pollution_df.to_sql('pollution', conn, if_exists='replace', index=False)
    emissions_df.to_sql('emissions', conn, if_exists='replace', index=False)
    conn.close()
    logger.info("Database operations completed")
    
    logger.info("Cleaning up temporary files")
    for file in temp_dir.glob('*'):
        file.unlink()
    temp_dir.rmdir()
    logger.info("Pipeline execution completed successfully")

if __name__ == "__main__":
    main()
