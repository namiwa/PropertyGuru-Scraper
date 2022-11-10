import argparse
import numpy as np
import pandas as pd
import phonenumbers
import pywhatkit
import os


NUMBERS_CACHE_FILE = './agent_numbers_cache.csv'


def clean_number(unclean_number: str):
    try:
        x = phonenumbers.parse(unclean_number, 'SG')
        return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        print(f'number parsing error: {e}', flush=True)
        return np.nan

def argsparser():
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('-f', '--file', dest='File', help='eg. path to csv file')
        parser.add_argument('-m', '--message', dest='Message', help='eg. custom message to be sent to agents')
        args = parser.parse_args()
        return args
    except:
        parser.print_help()
        exit()

def send_ws(args):
    print(args)
    number, author, link, prop_name, price = args
    msg = MESSAGE + f'\nI am interested for your listing: {link} for ${price} a month.\nIs it available?'
    pywhatkit.sendwhatmsg_instantly(number, msg, 8, tab_close=True)
    print(number, author, link, prop_name, price)

def main():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, converters={'AgentNumber': str})
        df['AgentNumber'] = df['AgentNumber'].copy().apply(clean_number)
        
        infoDf = df[['AgentNumber', 'Author', 'Link', 'PropertyName', 'Price']].copy()
        print(infoDf.head())
        infoDf.apply(send_ws, axis='columns')
    
    else:
        print('error encountered')
        exit(1)

if __name__ == "__main__":
    args = argsparser()
    FILE, MESSAGE = args.File, args.Message
    main()