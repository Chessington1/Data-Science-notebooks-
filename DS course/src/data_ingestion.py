import pandas as pd
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger("data_ingestion")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def create_db_engine(db_path: str):
    """
    Create a SQLAlchemy engine for the SQLite database.

    Parameters:
    db_path (str): Path to the SQLite database file, e.g., 'sqlite:///file.db'.

    Returns:
    engine: SQLAlchemy engine object
    """
    try:
        engine = create_engine(db_path)
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info("Database engine created successfully.")
        return engine
    except ImportError as e:
        logger.error("SQLAlchemy is required. Please install it first.")
        raise e
    except Exception as e:
        logger.error(f"Failed to create database engine. Error: {e}")
        raise e

def query_data(engine, sql_query: str):
    """
    Execute SQL query and return results as a Pandas DataFrame.

    Parameters:
    engine: SQLAlchemy engine object
    sql_query (str): SQL query to execute

    Returns:
    df (pd.DataFrame): Query results
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection)
        if df.empty:
            msg = "The SQL query returned an empty DataFrame."
            logger.error(msg)
            raise ValueError(msg)
        logger.info(f"Query executed successfully. Result shape: {df.shape}")
        return df
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise e

def read_from_web_CSV(url: str):
    """
    Read CSV data from a web URL into a Pandas DataFrame.

    Parameters:
    url (str): URL pointing to a CSV file

    Returns:
    df (pd.DataFrame): CSV data
    """
    try:
        df = pd.read_csv(url)
        if df.empty:
            msg = f"The CSV at {url} is empty."
            logger.error(msg)
            raise ValueError(msg)
        logger.info(f"CSV loaded successfully from {url}. Shape: {df.shape}")
        return df
    except pd.errors.EmptyDataError as e:
        logger.error(f"No data found at {url}.")
        raise e
    except Exception as e:
        logger.error(f"Failed to read CSV from {url}. Error: {e}")
        raise e
