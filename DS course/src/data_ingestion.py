"""
data_ingestion.py

This module contains functions to handle data ingestion for the Maji Ndogo farm survey project.
It includes functionality to:
- Create a SQLAlchemy database engine
- Query data from the database
- Read CSV data from web URLs

All functions include logging to track successful execution and errors.
"""

from sqlalchemy import create_engine, text
import logging
import pandas as pd

# Name our logger so we know that logs from this module come from the data_ingestion module
logger = logging.getLogger('data_ingestion')
# Set a basic logging message that prints timestamp, logger name, level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Default paths and URLs
db_path = 'sqlite:///Maji_Ndogo_farm_survey_small.db'

sql_query = """
SELECT *
FROM geographic_features
LEFT JOIN weather_features USING (Field_ID)
LEFT JOIN soil_and_crop_features USING (Field_ID)
LEFT JOIN farm_management_features USING (Field_ID)
"""

weather_data_URL = "https://raw.githubusercontent.com/Explore-AI/Public-Data/master/Maji_Ndogo/Weather_station_data.csv"
weather_mapping_data_URL = "https://raw.githubusercontent.com/Explore-AI/Public-Data/master/Maji_Ndogo/Weather_data_field_mapping.csv"


def create_db_engine(db_path):
    """
    Create a SQLAlchemy database engine.

    Parameters
    ----------
    db_path : str
        The database URI or path to the SQLite database file.

    Returns
    -------
    sqlalchemy.engine.base.Engine
        SQLAlchemy engine object for connecting to the database.

    Raises
    ------
    ImportError
        If SQLAlchemy is not installed.
    Exception
        If the engine could not be created for any other reason.
    """
    try:
        engine = create_engine(db_path)
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info("Database engine created successfully.")
        return engine
    except ImportError:  # If SQLAlchemy not installed
        logger.error("SQLAlchemy is required to use this function. Please install it first.")
        raise e
    except Exception as e:  # If engine creation fails
        logger.error(f"Failed to create database engine. Error: {e}")
        raise e


def query_data(engine, sql_query):
    """
    Execute a SQL query and return the results as a Pandas DataFrame.

    Parameters
    ----------
    engine : sqlalchemy.engine.base.Engine
        SQLAlchemy engine object.
    sql_query : str
        SQL query to execute.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the query results.

    Raises
    ------
    ValueError
        If the query returns an empty DataFrame.
    Exception
        If any other error occurs during the query execution.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection)
        if df.empty:
            msg = "The query returned an empty DataFrame."
            logger.error(msg)
            raise ValueError(msg)
        logger.info("Query executed successfully.")
        return df
    except ValueError as e:
        logger.error(f"SQL query failed. Error: {e}")
        raise e
    except Exception as e:
        logger.error(f"An error occurred while querying the database. Error: {e}")
        raise e


def read_from_web_CSV(URL):
    """
    Read a CSV file from a web URL and return it as a Pandas DataFrame.

    Parameters
    ----------
    URL : str
        URL pointing to the CSV file.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the CSV data.

    Raises
    ------
    pd.errors.EmptyDataError
        If the URL does not point to a valid CSV file.
    Exception
        If any other error occurs while reading the CSV.
    """
    try:
        df = pd.read_csv(URL)
        logger.info("CSV file read successfully from the web.")
        return df
    except pd.errors.EmptyDataError as e:
        logger.error("The URL does not point to a valid CSV file. Please check the URL and try again.")
        raise e
    except Exception as e:
        logger.error(f"Failed to read CSV from the web. Error: {e}")
        raise e
