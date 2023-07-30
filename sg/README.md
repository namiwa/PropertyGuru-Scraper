# A modified PropertyGuru Scraper for Singapore

## Installing steps for scraper
- Ensure that python3 is installed (last tested version was python 3.10.6)
- Ensure that git is installed on local machine (tested on Windows 10 & MacOS Montery)
- git clone this repo locally: `git clone https://github.com/namiwa/PropertyGuru-Scraper.git`
- install python deps: `pip install -r requirements.txt`
- change directory to the sg folder: `cd sg`
- Create an account on [Crawlbase](https://crawlbase.com), and take note of the [Smart Proxy Token](https://crawlbase.com/docs/smart-proxy/#how-it-works)
- edit the scraping script directly to select the relavent districts based on the states map
```python
westKeys = ["D21"] # line 58 of data-scraper-rent-sg.py
```
- run the following command, in the sg folder: `python data-scraper-rent-sg.py -m residential -t rent -maxp <MAX-PRICE> -minp <MIN-PRICE> -w 1 -k <CRAWLBASE-TOKEN>`
- help output 
```shell
(propgruru-22) namiwa/sg:[git:main] ~python data-scraper-rent-sg.py -h
usage: data-scraper-rent-sg.py [-h] [-m MARKET] [-t TYPE] [-maxp MAXPRICE] [-minp MINPRICE] [-w WEST] [-k TOKEN]

options:
  -h, --help            show this help message and exit
  -m MARKET, --market MARKET
                        eg. Residential, Commercial etc. (default: Condo)
  -t TYPE, --type TYPE  eg. Condo, Terrace, etc. (default: condo)
  -maxp MAXPRICE, --maxPrice MAXPRICE
                        eg. maximum price considered for rent
  -minp MINPRICE, --minPrice MINPRICE
                        eg. minimum price considered for rent
  -w WEST, --west WEST  eg. indicate whether west district is filtered
  -k TOKEN, --key TOKEN
                        Required api token from crawlbase
```

## Installing steps for Whatsapp automation
- Ensure that you have Whatsapp Web authenticated on your default browser (QR devices linked).
- Note that this will run to message every agent for every property in the data file provided, so its best to space out this automation, since it might result in a ban from Whatsapp if they were to detect anomalous activity.
- The data file provided is from the previous script, where a sample file path looks like `data/Nov2022/rent-Nov2022-listing-D03.csv`.
- Run the sample automation command: `python ws-automation.py -f <SAMPLE-DATA-FILE-PATH> -m "My name is Khairul Iman, and I am looking to rent a room for the period of Jan 23 - Dec 23."`
- Help message: 
```shell
(propgruru-22) namiwa/sg:[git:main] ~python ws-automation.py -h
usage: ws-automation.py [-h] [-f FILE] [-m MESSAGE]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  eg. path to csv file
  -m MESSAGE, --message MESSAGE
                        eg. custom message to be sent to agents
usage: ws-automation.py [-h] [-f FILE] [-m MESSAGE]

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  eg. path to csv file
  -m MESSAGE, --message MESSAGE
                        eg. custom message to be sent to agents
```
