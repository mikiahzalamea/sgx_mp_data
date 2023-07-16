# SGX Historical Files Downloader

Downloads the following files from the SGX Website:

WEBPXTICK_DT-*.zip  
TickData_structure.dat  
TC_*.txt  
TC_structure.dat  

## Description

The program is able to download files from the SGX Website including the files that are not listed in
the website (Older Files). The project is made in python and creates a log for the files downloaded 
and errors that may occur. The project also has a recovery plan by redownloading the files a certain
amount of times before deciding to stop. The amount of tries the program tries and the retry delay can be
changed in the config file.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

Before running the program please run the following commands

"pip install -r requirements.txt"

Please also change the "folder_path_base" in the config file if you wish to run the program with
a config file. The Config file is inside config_optional, please put it in the same folder as dtl_mp_data
to use it


## Usage

The project may be run automatically everyday to do so, it just needs to run the following

"python dtl_mp_data.py"

If you wish to download a date manually you may input it like a Linux command

"python dtl_mp_data.py yyyy-mm-dd"
ex. "python dtl_mp_data.py 2023-06-28"

## Contact

Mikiah Matthew T. Zalamea  
+(639)9985543986  
mikiah.zalamea@gmail.com  