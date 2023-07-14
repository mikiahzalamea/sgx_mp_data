from datetime import date, timedelta

# Adds the SGX Website as a variable to use to get Requests
URL_BASE = "https://www.sgx.com/research-education/derivatives"

# Key for the API 5455 = July 4, 2023 so we base everything off that
BASE_KEY = 5455
BASE_DATE = date(2023, 7, 4)

# YESTERDAY
YESTERDAY = date.today() - timedelta(days=1)

# FOLDER_PATH
FOLDER_PATH_BASE = "/home/mikiah/Coding/dtl_mp_data/"

# API URL
API_URL = "https://links.sgx.com/1.0.0/derivatives-historical/"
