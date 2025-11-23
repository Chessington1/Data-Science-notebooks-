import pandas as pd
import re
import logging

logger = logging.getLogger("weather_data_processor")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

patterns = {
    'Rainfall': r'(\d+(\.\d+)?)\s?mm',
    'Temperature': r'(\d+(\.\d+)?)\s?C',
    'Pollution_level': r'=\s*(-?\d+(\.\d+)?)|Pollution at \s*(-?\d+(\.\d+)?)'
}

class WeatherDataProcessor:
    """
    Class to clean and process weather station data.
    """

    def __init__(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError("Input weather DataFrame is empty.")
        self.df = df.copy()
        logger.info(f"WeatherDataProcessor initialized with {self.df.shape[0]} rows and {self.df.shape[1]} columns.")

    def extract_measurements(self, message_column="Message"):
        """
        Extract measurements (Rainfall, Temperature, Pollution) from messages using regex.
        """
        if message_column not in self.df.columns:
            raise KeyError(f"{message_column} not found in weather data.")

        def extract_measurement(message):
            for key, pattern in patterns.items():
                match = re.search(pattern, str(message))
                if match:
                    return key, float(next((x for x in match.groups() if x is not None)))
            return None, None

        result = self.df[message_column].apply(extract_measurement)
        self.df['Measurement'] = result.apply(lambda x: x[0])
        self.df['Value'] = result.apply(lambda x: x[1])
        logger.info("Extracted measurements into 'Measurement' and 'Value' columns.")
        return self

    def compute_station_means(self, station_column="Weather_station_ID"):
        """
        Compute mean value per station and measurement type.
        """
        if station_column not in self.df.columns:
            raise KeyError(f"{station_column} not found in weather data.")

        self.df = self.df.groupby([station_column, 'Measurement'])['Value'].mean(numeric_only=True).unstack()
        logger.info(f"Computed mean values per station. Result shape: {self.df.shape}")
        return self

    def fill_missing(self, strategy="mean"):
        """
        Fill missing values with the chosen strategy.
        """
        for col in self.df.columns:
            if strategy == "mean":
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == "median":
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif strategy == "zero":
                self.df[col] = self.df[col].fillna(0)
            else:
                raise ValueError("Strategy must be 'mean', 'median', or 'zero'.")
        logger.info(f"Filled missing values using strategy '{strategy}'.")
        return self
