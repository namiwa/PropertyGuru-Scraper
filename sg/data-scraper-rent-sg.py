import time
import cloudscraper
import numpy as np
import pandas as pd
import os
import hashlib
import argparse
import ssl
from typing import List
from bs4 import BeautifulSoup
from datetime import date
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
disable_warnings(category=InsecureRequestWarning)
# https://stackoverflow.com/a/67924139/13941170

# Default Query parameter
MARKET = 'residential'
TYPE = 'rent'

### CODE STARTS HERE ###

state = {
    'D01': 'D01 Boat Quay / Raffles Place / Marina',
    'D02': 'D02 Chinatown / Tanjong Pagar',
    'D03': 'D03 Alexandra / Commonwealth',
    'D04': 'D04 Harbourfront / Telok Blangah',
    'D05': 'D05 Buona Vista / West Coast / Clementi New Town',
    'D06': 'D06 City Hall / Clarke Quay',
    'D07': 'D07 Beach Road / Bugis / Rochor',
    'D08': 'D08 Farrer Park / Serangoon Rd',
    'D09': 'D09 Orchard / River Valley',
    'D10': 'D10 Tanglin / Holland / Bukit Timah',
    'D11': 'D11 Newton / Novena',
    'D12': 'D12 Balestier / Toa Payoh',
    'D13': 'D13 Macpherson / Potong Pasir',
    'D14': 'D14 Eunos / Geylang / Paya Lebar',
    'D15': 'D15 East Coast / Marine Parade',
    'D16': 'D16 Bedok / Upper East Coast',
    'D17': 'D17 Changi Airport / Changi Village',
    'D18': 'D18 Pasir Ris / Tampines',
    'D19': 'D19 Hougang / Punggol / Sengkang',
    'D20': 'D20 Ang Mo Kio / Bishan / Thomson',
    'D21': 'D21 Clementi Park / Upper Bukit Timah',
    'D22': 'D22 Boon Lay / Jurong / Tuas',
    'D23': 'D23 Dairy Farm / Bukit Panjang / Choa Chu Kang',
    'D24': 'D24 Lim Chu Kang / Tengah',
    'D25': 'D25 Admiralty / Woodlands',
    'D26': 'D26 Mandai / Upper Thomson',
    'D27': 'D27 Sembawang / Yishun',
    'D28': 'D28 Seletar / Yio Chu Kang'
}
allKeys = [key for key in state.keys()]
all = f'{"".join([f"&district_code[]={key}" for key in allKeys])}&freetext={"".join(f"{state[key]}," for key in allKeys)}'
# areas near west (NUS) "D03", "D04", "D05", "D10", "D21"
westKeys = ["D21"]
west = f'{"".join([f"&district_code[]={key}" for key in westKeys])}&freetext={"".join(f"{state[key]}," for key in westKeys)}'

def BSPrep(URL):
    exitcode = 1
    while exitcode == 1:
        try:
            trial = 0
            while trial < 10:
                print('Loading ' + URL)
                proxies={"http": f"http://{TOKEN}:@smartproxy.crawlbase.com:8012", "https": f"http://{TOKEN}:@smartproxy.crawlbase.com:8012"}
                ssl_context = ssl.create_default_context()
                ssl_context.load_default_certs()
                ssl_context.check_hostname = False
                scraper = cloudscraper.create_scraper(interpreter='nodejs', ssl_context=ssl_context)
                response = scraper.get(URL, proxies=proxies, verify=False)
                soup = BeautifulSoup(response.content, 'html.parser')
                if "captcha" in soup.text:
                    trial += 1
                    print('Retrying '+' ('+str(trial)+'/10) ...')
                    time.sleep(0.1)
                    continue
                elif "No Results" in soup.text:
                    print('Invalid URL, skipping '+URL)
                    trial = 99
                else:
                    trial = 99
            if trial == 10:
                print('Trial exceeded, skipping '+URL)
            exitcode = 0
            return soup
        except Exception as e:
                print(e, flush=True)
                print('Connection reset, retrying in 1 mins...', flush=True)
                time.sleep(60)
        
def Pagination(soup):
    pagination = soup.find("ul", class_="pagination")
    try:
        if pagination.find_all("li", class_="pagination-next disabled"):
            pages = int(pagination.find_all("a")[0]['data-page'])
        else:
            pages = int(pagination.find_all("a")[-2]['data-page'])
    except AttributeError:
        if soup.find("h1", class_="title search-title").text.split(' ')[2] == '0':
            print('No property found. Scraping stopped.')
            exit(0)
        else:
            exit(1)
    return pages

def LinkScraper(soup):
    links = []
    units = soup.find_all("div", itemtype="https://schema.org/Place")
    for unit in units:
        if unit.find("a", class_="btn btn-primary-outline units_for_sale disabled") and unit.find("a", class_="btn btn-primary-outline units_for_rent disabled"):
            continue
        prop = unit.find("a", class_="nav-link")
        links.append((prop['title'],HEADER+prop["href"]))
    return(links)

def InfoExtract(pname, soup: BeautifulSoup, key, link):
    page_listing = []
    i = -1 if 'sale' in key else 0
    type = 'Sale' if 'sale' in key else 'Rent'
    keys: List[BeautifulSoup] = soup.find_all(itemtype="https://schema.org/Accommodation https://schema.org/Product")
    for property in keys:
        try:
            bed = property.find('span', itemprop="numberOfRooms").get_text(strip=True)
        except:
            bed = np.nan
        
        try:
            bathElem = property.find('div', class_='baths')
            bath = bathElem.find('span', class_='element-label').get_text(strip=True)
        except:
            bath = np.nan

        try:
            price = property.find("span", itemprop="price").attrs.get('content')
        except:
            price = np.nan

        try:
            sqftElem = property.find("div", itemtype="https://schema.org/QuantitativeValue")
            sqft = sqftElem.find("meta", itemprop="value").attrs.get('content')
        except:
            sqft = np.nan

        try:
            agentInfo = property.find('div', class_='agent-details-container')
            author = agentInfo.find('a', class_='agent-profile-redirect').getText(strip=True)
        except:
            author = np.nan

        try:
            agent_number_raw = property.find_all('span', class_="agent-phone-number")
            print(f'check: {agent_number_raw}')
            agent_number_raw = agent_number_raw[0].get_text(strip=True)
            agent_number = "".join(agent_number_raw.split())
        except:
            agent_number = np.nan

        try:
            addressElem = property.find('div', itemtype="https://schema.org/PostalAddress")
            streetAddress = addressElem.find('span', itemprop="streetAddress").get_text(strip=True)
            postalCode = addressElem.find('span', itemprop="postalCode").get_text(strip=True)
        except:
            streetAddress = np.nan
            postalCode = np.nan
        
        try:
            name = property.find('h1', itemprop='name').text.strip()
        except:
            name = np.nan

        data = [pname, type, price, bed, bath, sqft, author, name, streetAddress, postalCode, agent_number, link]
        page_listing.append(data)

    return page_listing

def PropScrapper(pname, plink, key):
    prop_listing = []
    link = HEADER + plink.replace(HEADER, "")
    soup = BSPrep(link)
    prop_listing += InfoExtract(pname, soup, key, link)
    return prop_listing

def md5hash(datafile, hashfile):
    h = hashlib.md5()
    with open(datafile,'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    with open(hashfile, 'w') as f:
        f.write(h.hexdigest())
    print('MD5 hash generated to '+hashfile)

def PropTrimmer(props, datafile):
    df_old = pd.read_csv(datafile)
    prop, link = zip(*props)
    len_old_props = len(prop)
    last_prop_name = df_old.PropertyName.iat[-1]
    prop_index = prop.index(last_prop_name)
    props = props[prop_index:]
    print('This is a re-run.\nSkipping {} properties scraped previously.'.format(len_old_props-len(props)))
    return props, last_prop_name

def argparser():
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('-m', '--market', default=MARKET, dest='Market', help='eg. Residential, Commercial etc. (default: Condo)')
        parser.add_argument('-t', '--type', default=TYPE, dest='Type', help='eg. Condo, Terrace, etc. (default: condo)')
        parser.add_argument('-mp', '--maxPrice', default='1500', dest='MaxPrice', help='eg. max price considering for rent')
        parser.add_argument('-w', '--west', default=True, dest="West", help='eg. indicate whether west district is filtered')
        parser.add_argument('-k', '--key', dest="Token", help='Required api token from crawlbase')
        args = parser.parse_args()
        return args
    except:
        parser.print_help()
        exit()

def main():
    
    # Load first page with Query and scrape no. of pages
    print('\n===================================================\nPropertyGuru Property Listing Scraper v2.4-alpha\nAuthor: DicksonC , modified by namiwa for SG\n===================================================\n')
    time.sleep(2)
    print('Job initiated with query on {}.'.format(TYPE))
    print('\nLoading '+HEADER+KEY+QUERY+' ...\n')
    soup = BSPrep(HEADER+KEY+QUERY)
    pages = Pagination(soup)
    print(str(pages)+' page will be scrapped.\n')

    # Scrape links from first page for properties with both sale and rental listing
    props = []
    props += LinkScraper(soup)
    print('\rPage 1/{} done.'.format(str(pages)))

    # Scrape subsequent pages
    for page in range(2, pages+1):
        soup = BSPrep(HEADER+KEY+'/'+str(page)+QUERY)
        props += LinkScraper(soup)
        print('\rPage {}/{} done.'.format(str(page), str(pages)))

    # Check exising data and remove scraped links
    if os.path.exists(RAW_LISTING):
        try:
            props, last_prop_name = PropTrimmer(props, RAW_LISTING)
            error_flag = False
        except ValueError or IndexError:
            print("EOF does not match. Scraping starts from the beginning.")
            error_flag = True
    
    # Scrape details for rental of each properties
    data = []
    print('\nA total of '+str(len(props))+' properties will be scraped.\n')
    columns = ['PropertyName','Type','Price','Bedrooms','Bathrooms','Sqft','Author', 'Title', 'StreetAddress', 'PostalCode', 'AgentNumber', 'Link']

    try:
        for i, prop in enumerate(props):
            name, url = prop
            url = HEADER + url.replace(HEADER, "")
            rent = PropScrapper(name, url, '/property-for-rent')
            print(f'starting property: {name}-{url}-{rent}')
            print(str(i+1)+'/'+str(len(props))+' done!')
            data += rent
        
        # Result into DataFrame and Analysis
        df = pd.DataFrame(data, columns=columns)

        # Check if data directory exists
        if not os.path.isdir(LIST_DIR):
            os.makedirs(LIST_DIR)

        # Check exising data and combine
        if os.path.exists(RAW_LISTING):
            if not error_flag:
                df_old = pd.read_csv(RAW_LISTING)
                df_old = df_old[df_old.PropertyName!=last_prop_name]
                df = pd.concat([df_old, df])

        # Raw data saved to file
        df.to_csv(RAW_LISTING, index=False)
        print('Raw data saved to {}'.format(RAW_LISTING))

    except Exception as e:
        print(e)
        print('Error encountered! Exporting current data ...')

        # Result into DataFrame and Analysis
        df = pd.DataFrame(data, columns=columns)

        # Check if data directory exists
        if not os.path.isdir(LIST_DIR):
            os.makedirs(LIST_DIR)

        # Raw data saved to file
        df.to_csv(RAW_LISTING, index=False)
        print('INCOMPLETE raw data saved to {}'.format(RAW_LISTING))
        exit(1)

    else:
        # Check if hash directory exists
        if not os.path.isdir(HASH_DIR):
            os.makedirs(HASH_DIR)

        md5hash(RAW_LISTING, MD5HASH)

if __name__ == "__main__":

    # Initialize arguments
    args = argparser()
    MARKET, TYPE, MAXPRICE, WEST, TOKEN = args.Market, args.Type, args.MaxPrice, args.West, args.Token
    districts = "".join(westKeys) if WEST else "-".join(allKeys)
    # Initialize filenames (leave empty if not generating)
    LIST_DIR = './data/{}'.format(date.today().strftime("%b%Y"))
    HASH_DIR = './md5hash/{}'.format(date.today().strftime("%b%Y"))
    RAW_LISTING = './data/{}/{}-{}-listing-{}.csv'.format(date.today().strftime("%b%Y"),TYPE,date.today().strftime("%b%Y"),districts)
    MD5HASH = './md5hash/{}/{}-{}-listing-{}.md5'.format(date.today().strftime("%b%Y"),TYPE,date.today().strftime("%b%Y"),districts)

    # Initialize URL
    HEADER = 'https://www.propertyguru.com.sg/'
    QUERY = '?market='+MARKET.lower()+f'&listing_type{TYPE}'+'&search=true'+f'&maxprice={MAXPRICE}'
    if (WEST):
        QUERY = QUERY + west
    else:
        QUERY = QUERY + all
    
    KEY = 'property-for-rent'

    main()
