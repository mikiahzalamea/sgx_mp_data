import requests
import sys
import os
from requests.adapters import HTTPAdapter
import urllib.request
from urllib3.util.retry import Retry
from urllib.request import urlretrieve
import time
import datetime
import logging
import logging.handlers
from datetime import timedelta
import argparse
import configparser
from dateutil.parser import parse
from settings import BASE_KEY, BASE_DATE, YESTERDAY, FOLDER_PATH_BASE,API_URL

# Root Logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a file handler to log to a file
file_handler = logging.FileHandler('sgx_files.log')
file_handler.setLevel(logging.DEBUG)

# Create a stream handler to log to stdout
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', '%H:%M:%S')

# Set the formatter for the handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Create a filter for the stream handler
stream_filter = logging.Filter()
stream_filter.filter = lambda record: record.levelno <= logging.warning

# Set the filter for the stream handler
stream_handler.addFilter(stream_filter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Allows the user to specify the date of the files they wish to download in the CLI
parser = argparse.ArgumentParser(description="Downloads SGX Time and Sales Historical Data")
parser.add_argument('date', metavar='date', type=parse, nargs='?', help="Enter the date of the files you wish to download in the format yyyy-mm-dd")
args = parser.parse_args()

# Create Config
config = configparser.ConfigParser()
config_file = 'config.ini'

# Function to ensure that the date is valid if ran with default settings
def weekday_checker(date_variable):
    if date_variable.weekday() == 0:  #Monday to Friday (0 to 4)
        logging.info("Today is Monday, there is no Data to download from the day before, the program will download last friday's files")
        return date_variable - datetime.timedelta(days=2) # If monday return friday
    elif 0 < date_variable.weekday() < 6:
        return date_variable
    else:
        logging.debug("Today is Sunday, there is no Data to download from the day before")
        sys.exit(1)

# Manually download the files on a specific date
if args.date:
    date_variable = args.date.date()
else:
    date_variable = weekday_checker(YESTERDAY)  #Downloads the file yesterday AKA Default settings

try:
    config.read(config_file)
    # Read the max_retries and retry_delay values from the config file
    max_retries = config.getint('Default', 'max_retries')
    retry_delay = config.getint('Default', 'retry_delay')

except (FileNotFoundError, configparser.Error):
    # Handle the case where the config file is not found or there is an error reading it
    logging.debug("Config file not found or error reading config file. Using default values.")
    # Set default values or fallback behavior here
    max_retries = 3  # Set a default value for max_retries
    retry_delay = 1  # Set a default value for retry_delay

def count_business_days(start_date, end_date):
    """
    Calculates the number of business days between two given dates.

    Parameters:
        start_date (datetime.date): The starting date.
        end_date (datetime.date): The ending date.

    Returns:
        int: The number of business days between the two dates.
    """
    # Initialize count and current_date variables
    count = 0
    current_date = start_date

    # Check if end_date is earlier than start_date
    if end_date < start_date:
        return (end_date - start_date).days
    
    # Check if current_date is equal to end_date
    elif current_date == end_date:
        return 0
    
    # Check if end_date is in the future
    elif end_date >= datetime.date.today():
        logging.error("The date you wish to download is too far into the future")

    # Loop through each date from start_date to end_date
    while current_date <= end_date:
        # Increment count if current_date is a weekday (Monday to Friday)
        if current_date.weekday() < 5:
            count += 1
        current_date += timedelta(days=1)

    return count

# Take out the hyphens from the date for the file name
date_fn = str(date_variable).replace("-","")
# Algorithm to compute for the key of each file
key  = BASE_KEY + count_business_days(BASE_DATE, date_variable) - 1
# Folder path algorithm
FOLDER_PATH = FOLDER_PATH_BASE +"{date}/".format(date = date_variable)

# Function to download the files from the URL with a set amount of retries if it fails to download
def download_files(file_name, url, folder_path, max_retries, retry_delay):
    """
    Downloads a file from a given URL and saves it to the specified folder path.
    
    Args:
        file_name (str): The name of the file to be downloaded.
        url (str): The URL of the file to be downloaded.
        folder_path (str): The path where the file will be saved.
        max_retries (int): The maximum number of download retries.
        retry_delay (int): The delay between download retries in seconds.
    """
    # Make the folder for the day if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # File Path name algorithm
    file_path = os.path.join(folder_path, file_name)
    
    session = requests.Session()
    retries = 0
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        # Downloads the File from the URL with the name specified as file_path
        urlretrieve(url, file_path)
        logging.info(f"{file_name} downloaded and saved successfully.")
        # Exit function if download is successful
        return
    except Exception as e:
        retries += 1
        error_message = f"Download failed (Retry {retries}): {str(e)}"
        logging.error(f"The download failed for {file_name} with the error: {error_message} after {retries} retries. Please manually download the files another time.")
        time.sleep(retry_delay)

# Links that download the files
tick = API_URL + "{key}/WEBPXTICK_DT-{date_fn}.zip".format(key=key, date_fn = date_fn)
tick_data_structure =API_URL + "{key}/TickData_structure.dat".format(key=key)
trade_cancellation = API_URL + "{key}/TC.txt".format(key=key)
trade_cancellation_data_structure = API_URL + "{key}/TC_structure.dat".format(key=key)

# File names for the files downloaded
tick_fn = "WEBPXTICK_DT-{date_fn}.zip".format(date_fn = date_fn)
tick_data_structure_fn = "TickData_structure.dat"
trade_cancellation_fn = "TC_{date_fn}.txt".format(date_fn = date_fn)
trade_cancellation_data_structure_fn = "TC_structure.dat"

download_files(tick_fn, tick, FOLDER_PATH, max_retries, retry_delay)
download_files(tick_data_structure_fn, tick_data_structure, FOLDER_PATH, max_retries, retry_delay)
download_files(trade_cancellation_fn, trade_cancellation, FOLDER_PATH, max_retries, retry_delay)
download_files(trade_cancellation_data_structure_fn, trade_cancellation_data_structure, FOLDER_PATH, max_retries, retry_delay)

