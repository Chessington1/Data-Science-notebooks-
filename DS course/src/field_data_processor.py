import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging

logger = logging.getLogger("field_data_processor")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class FieldDataProcessor:
    """
    Class to fetch, clean, and process field survey data.
    """

    def __init__(self, df: pd.DataFrame = None):
        """
        Initialize with a DataFrame (optional). If df is None, you can use ingest_sql_data to fetch it.
        """
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.engine = None
        logger.info(f"FieldDataProcessor initialized with "
                    f"{self.df.shape[0]} rows and {self.df.shape[1]} columns.")

        # Mapping for crop type corrections
        self.crop_corrections = {'cassaval': 'cassava', 'wheatn': 'wheat', 'teaa': 'tea'}

        # Column renaming mapping
        self.columns_to_swap = {'Annual_yield': 'Crop_type', 'Crop_type': 'Annual_yield'}

        # Database path and query
        self.db_path = 'sqlite:///Maji_Ndogo_farm_survey_small.db'
        self.sql_query = """
            SELECT *
            FROM geographic_features
            LEFT JOIN weather_features USING (Field_ID)
            LEFT JOIN soil_and_crop_features USING (Field_ID)
            LEFT JOIN farm_management_features USING (Field_ID)
        """

    def ingest_sql_data(self):
        """
        Connects to the database, queries the field data, and stores it in self.df.
        Returns the DataFrame.
        """
        try:
            # Create engine
            self.engine = create_db_engine(self.db_path)
            logger.info("Database engine created successfully.")

            # Query data
            self.df = query_data(self.engine, self.sql_query)
            logger.info(f"Successfully loaded data. Shape: {self.df.shape}")

            return self.df
        except Exception as e:
            logger.error(f"Failed to ingest SQL data: {e}")
            raise e
    
    def rename_columns(self):
        """
        Rename columns according to the notebook's corrections (swap Annual_yield and Crop_type).
        """
        if 'Annual_yield' in self.df.columns and 'Crop_type' in self.df.columns:
            self.df.rename(columns={'Annual_yield': 'Crop_type_Temp', 'Crop_type': 'Annual_yield'}, inplace=True)
            self.df.rename(columns={'Crop_type_Temp': 'Crop_type'}, inplace=True)
            logger.info("Columns renamed: Annual_yield <-> Crop_type")
        return self

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):
        self.df[abs_column] = self.df[abs_column].abs()
        self.df[column_name] = self.df[column_name].apply(
            lambda crop: self.values_to_rename.get(crop, crop)
        )

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
            self.df[column] = self.df[column].str.strip().replace(self.crop_corrections)
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
