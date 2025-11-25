"""
weather_data_processor.py

This module contains the WeatherDataProcessor class which handles
all weather-related data processing for the Maji Ndogo farm survey project.

Features:
- Load weather station CSV from web
- Extract numeric measurements from message strings using regex
- Process extracted measurements into structured columns
- Calculate mean values grouped by station and measurement type
"""

import re
import pandas as pd
import logging
from data_ingestion import read_from_web_CSV


class WeatherDataProcessor:
    def __init__(self, config_params, logging_level="INFO"):
        """
        Initialize the WeatherDataProcessor.

        Parameters
        ----------
        config_params : dict
            Configuration dictionary containing:
                - weather_csv_path : URL to weather station CSV
                - regex_patterns : dictionary of regex patterns
        logging_level : str, optional
            Logging level ("DEBUG", "INFO", "NONE"), by default "INFO"
        """
        self.weather_station_data = config_params['weather_csv_path']
        self.patterns = config_params['regex_patterns']
        self.weather_df = None
        self.initialize_logging(logging_level)

    def initialize_logging(self, logging_level):
        """
        Set up logger for the class.
        """
        logger_name = __name__ + ".WeatherDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False

        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO

        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def weather_station_mapping(self):
        """
        Load weather station CSV from the web.
        """
        self.weather_df = read_from_web_CSV(self.weather_station_data)
        self.logger.info("Successfully loaded weather station data from the web.")

    def extract_measurement(self, message):
        """
        Extract numeric measurement from a message string using regex.

        Parameters
        ----------
        message : str
            Text message containing measurement.

        Returns
        -------
        tuple
            (Measurement type, value) or (None, None) if no match.
        """
        for key, pattern in self.patterns.items():
            match = re.search(pattern, message)
            if match:
                return key, float(next((x for x in match.groups() if x is not None)))
        return None, None

    def process_messages(self):
        """
        Apply extract_measurement to all messages in the weather dataframe.
        """
        if self.weather_df is not None:
            result = self.weather_df['Message'].apply(self.extract_measurement)
            self.weather_df['Measurement'], self.weather_df['Value'] = zip(*result)
            self.logger.info("Messages processed and measurements extracted.")
        else:
            self.logger.warning("weather_df not initialized, skipping message processing.")
        return self.weather_df

    def calculate_means(self):
        """
        Calculate mean values grouped by Weather_station_ID and Measurement.

        Returns
        -------
        pd.DataFrame
            Pivoted DataFrame with mean values for each measurement per station.
        """
        if self.weather_df is not None:
            means = self.weather_df.groupby(
                ['Weather_station_ID', 'Measurement']
            )['Value'].mean()
            self.logger.info("Mean values calculated.")
            return means.unstack()
        else:
            self.logger.warning("weather_df not initialized, cannot calculate means.")
            return None

    def process(self):
        """
        Full pipeline to load, process, and extract measurements from weather data.
        """
        self.weather_station_mapping()
        self.process_messages()
        self.logger.info("Weather data processing completed.")
        return self.weather_df
