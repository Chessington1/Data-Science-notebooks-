import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging

logger = logging.getLogger("field_data_processor")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class FieldDataProcessor:
    """
    Class to fetch, clean, and process field survey data.
    """

    def __init__(self, df: pd.DataFrame = None):
        """
        Initialize with a DataFrame (optional).
        If df is None, ingest_sql_data() will load it from the database.
        """
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.engine = None

        # Mapping for crop type typo corrections
        self.crop_corrections = {'cassaval': 'cassava', 'wheatn': 'wheat', 'teaa': 'tea'}

        # Column swap map
        self.columns_to_swap = {'Annual_yield': 'Crop_type', 'Crop_type': 'Annual_yield'}

        # SQL database configuration
        self.db_path = 'sqlite:///Maji_Ndogo_farm_survey_small.db'
        self.sql_query = """
            SELECT *
            FROM geographic_features
            LEFT JOIN weather_features USING (Field_ID)
            LEFT JOIN soil_and_crop_features USING (Field_ID)
            LEFT JOIN farm_management_features USING (Field_ID)
        """
        
        # Weather mapping URL
        self.weather_map_data = "https://raw.githubusercontent.com/Explore-AI/Public-Data/master/Maji_Ndogo/Weather_data_field_mapping.csv"

        logger.info(f"FieldDataProcessor initialized with {self.df.shape[0]} rows and {self.df.shape[1]} columns.")

    # -------------------------
    # DATA INGESTION
    # -------------------------
    def ingest_sql_data(self):
        """Connect to SQLite database and load field survey data."""
        try:
            self.engine = create_db_engine(self.db_path)
            logger.info("Database engine created successfully.")

            self.df = query_data(self.engine, self.sql_query)
            logger.info(f"Successfully loaded data. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Failed to ingest SQL data: {e}")
            raise e

    # -------------------------
    # CLEANING METHODS
    # -------------------------
    def rename_columns(self):
        """Swap Annual_yield <-> Crop_type."""
        if 'Annual_yield' in self.df.columns and 'Crop_type' in self.df.columns:
            self.df.rename(columns={'Annual_yield': 'Crop_type_Temp', 'Crop_type': 'Annual_yield'}, inplace=True)
            self.df.rename(columns={'Crop_type_Temp': 'Crop_type'}, inplace=True)
            logger.info("Columns renamed: Annual_yield <-> Crop_type")
        return self

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):
        """Fix crop type typos & turn elevation into absolute values."""
        if abs_column in self.df.columns:
            self.df[abs_column] = self.df[abs_column].abs()
        if column_name in self.df.columns:
            self.df[column_name] = self.df[column_name].astype(str).str.strip().replace(self.crop_corrections)
        logger.info("Applied corrections: elevation cleaned & crop types fixed.")
        return self

    def drop_unnecessary_columns(self):
        """Drop all automatically generated 'Unnamed' columns."""
        cols_to_drop = [col for col in self.df.columns if "Unnamed" in col]
        if cols_to_drop:
            self.df.drop(columns=cols_to_drop, inplace=True)
            logger.info(f"Dropped columns: {cols_to_drop}")
        return self

    def merge_with_weather_mapping(self, weather_mapping_df: pd.DataFrame):
        """Merge field dataframe with weather mapping DataFrame on Field_ID."""
        if weather_mapping_df.empty:
            raise ValueError("Weather mapping DataFrame is empty.")
        self.df = self.df.merge(weather_mapping_df, on="Field_ID", how="left")
        logger.info(f"Merged field data with weather mapping. New shape: {self.df.shape}")
        return self

    def weather_station_mapping(self):
        """Fetch weather mapping CSV from the web and return DataFrame."""
        weather_df = read_from_web_CSV(self.weather_map_data)
        logger.info(f"Weather mapping CSV loaded. Shape: {weather_df.shape}")
        return weather_df

    # -------------------------
    # FULL PROCESS PIPELINE
    # -------------------------

    def process(self):
        # Load data if empty
        if self.df.empty:
            self.ingest_sql_data()

        # Step 1: rename columns
        self.rename_columns()

        # Step 2: fix typos & elevation
        self.apply_corrections()

        # Step 3: drop unnecessary columns
        self.drop_unnecessary_columns()

        # Step 4: merge weather mapping
        weather_df = self.weather_station_mapping()
        self.merge_with_weather_mapping(weather_df)

        logger.info("Full processing pipeline complete.")
        return self.df