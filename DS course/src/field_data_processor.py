import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging

logger = logging.getLogger("field_data_processor")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class FieldDataProcessor:
    """
    Class to clean and process field survey data.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a DataFrame.
        """
        if df.empty:
            raise ValueError("Input field DataFrame is empty.")
        self.df = df.copy()
        logger.info(f"FieldDataProcessor initialized with {self.df.shape[0]} rows and {self.df.shape[1]} columns.")

    def rename_columns(self):
        """
        Rename columns according to the notebook's corrections.
        """
        if 'Annual_yield' in self.df.columns and 'Crop_type' in self.df.columns:
            self.df.rename(columns={'Annual_yield': 'Crop_type_Temp', 'Crop_type': 'Annual_yield'}, inplace=True)
            self.df.rename(columns={'Crop_type_Temp': 'Crop_type'}, inplace=True)
            logger.info("Columns renamed: Annual_yield <-> Crop_type")
        return self

    def fix_elevation(self):
        """
        Convert elevation values to absolute values.
        """
        if 'Elevation' in self.df.columns:
            self.df['Elevation'] = self.df['Elevation'].abs()
            logger.info("Elevation values converted to absolute.")
        return self

    def correct_crop_type(self, column='Crop_type'):
        """
        Fix typos in crop type column.
        """
        if column in self.df.columns:
            corrections = {'cassaval': 'cassava', 'wheatn': 'wheat', 'teaa': 'tea'}
            self.df[column] = self.df[column].str.strip().replace(corrections)
            logger.info(f"Crop type corrected in column '{column}'.")
        return self

    def drop_unnecessary_columns(self):
        """
        Drop columns with 'Unnamed' in their name.
        """
        cols_to_drop = [col for col in self.df.columns if "Unnamed" in col]
        if cols_to_drop:
            self.df.drop(columns=cols_to_drop, inplace=True)
            logger.info(f"Dropped columns: {cols_to_drop}")
        return self

    def merge_with_weather_mapping(self, weather_mapping_df: pd.DataFrame):
        """
        Merge field data with weather mapping DataFrame on Field_ID.
        """
        if weather_mapping_df.empty:
            raise ValueError("Weather mapping DataFrame is empty.")
        self.df = self.df.merge(weather_mapping_df, on="Field_ID", how="left")
        logger.info(f"Merged field data with weather mapping. New shape: {self.df.shape}")
        return self
