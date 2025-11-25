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

    def __init__(self, config_params, df: pd.DataFrame = None):
        """
        Initialize with config parameters and optional DataFrame.
        """
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.engine = None

        # Pull everything from config_params
        self.db_path = config_params["db_path"]
        self.sql_query = config_params["sql_query"]
        self.columns_to_swap = config_params["columns_to_rename"]
        self.crop_corrections = config_params["values_to_rename"]
        self.weather_map_data = config_params["weather_mapping_csv"]

        logger.info(
            f"FieldDataProcessor initialized with "
            f"{self.df.shape[0]} rows and {self.df.shape[1]} columns."
        )

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
        col1, col2 = list(self.columns_to_swap.keys())[0], list(self.columns_to_swap.values())[0]

        if col1 in self.df.columns and col2 in self.df.columns:
            self.df.rename(columns={col1: "TEMP_COL"}, inplace=True)
            self.df.rename(columns={col2: col1}, inplace=True)
            self.df.rename(columns={"TEMP_COL": col2}, inplace=True)

            logger.info(f"Columns renamed: {col1} <-> {col2}")

        return self

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):
        """Fix crop type typos & turn elevation into abs values."""
        if abs_column in self.df.columns:
            self.df[abs_column] = self.df[abs_column].abs()

        if column_name in self.df.columns:
            self.df[column_name] = (
                self.df[column_name]
                .astype(str)
                .str.strip()
                .replace(self.crop_corrections)
            )

        logger.info("Applied corrections: elevation cleaned & crop types fixed.")
        return self

    def drop_unnecessary_columns(self):
        """Drop all automatically generated 'Unnamed' columns."""
        cols_to_drop = [col for col in self.df.columns if "Unnamed" in col]

        if cols_to_drop:
            self.df.drop(columns=cols_to_drop, inplace=True)
            logger.info(f"Dropped columns: {cols_to_drop}")

        return self

    # -------------------------
    # WEATHER MAPPING
    # -------------------------
    def weather_station_mapping(self):
        """Fetch weather mapping CSV from web and merge it."""
        weather_df = read_from_web_CSV(self.weather_map_data)
        logger.info(f"Weather mapping CSV loaded. Shape: {weather_df.shape}")

        if not self.df.empty:
            self.df = self.df.merge(weather_df, on="Field_ID", how="left")
            logger.info(f"Field data merged with weather mapping. New shape: {self.df.shape}")

        return self.df

    # -------------------------
    # FULL PROCESS PIPELINE
    # -------------------------
    def process(self):
        """
        Run the full cleaning and merging pipeline:
        1. Ingest SQL data
        2. Rename columns
        3. Apply corrections
        4. Drop unnecessary columns
        5. Merge weather mapping
        """
        self.ingest_sql_data()
        self.rename_columns()
        self.apply_corrections()
        self.drop_unnecessary_columns()
        self.weather_station_mapping()  # <-- Added merge directly here

        logger.info("Full processing pipeline complete.")
        return self.df
