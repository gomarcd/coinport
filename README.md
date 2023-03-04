# coinport
A minimalist cryptocurrency & portfolio tracker written in Python using the CoinGecko API.

## Requirements

**Python**

This is a Python script, so make sure you have Python installed. This was tested with Python 3.9 in Linux, Mac and Windows.

**Dependencies**

A few things are required in order to run this script. After installing Python, install them as follows. While not required, it is a good practice to also do this within a virtual environment:

`pip install pycoingecko pandas tabulate xlrd pyexcel_ods openpyxl sty`

Depending on your environment, you may need to type `python3` and `pip3` instead of `python` or `pip`.

## Windows

Some Windows 11 users have noticed that simply git cloning the repo and running the script resulted in errors about `.deleteme logic` and permissions errors. If that happens, try making sure your terminal is launched with *Run as Administrator* before following the steps, and be sure to also do `python -m pip install --upgrade pip`, then install the dependencies.


## Usage

LibreOffice and MS Office formats are supported. By default, the script will look for the included file, `crypto.xlsx`. You can point it to your file of choice by editing `conf.json` accordingly. When adding or removing coins from your spreadsheet, be sure to use the cryptocurrency name (ie, "Bitcoin", "Bitcoin Cash", "Synthetix Network Token"). The ticker/symbol is not used here because there are many duplicates. You may also specify the currency and add/remove columns in the conf file:

![screenshot](screenshot_conf.png)

Download ZIP above or just git clone the repo:

`git clone https://github.com/zcyph/coinport`

Change to the directory you just downloaded into, ie:

`cd coinport`

Run the script:

`python coinport.py`

The script will stay running and automatically refresh prices and changes to the configuration. To stop the script, press `CTRL-C` or close the terminal window.


![screenshot](screenshot.png)
