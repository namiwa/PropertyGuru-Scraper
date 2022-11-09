import argparse
import numpy as np
import pandas as pd
import phonenumbers
import pywhatkit
import os


NUMBERS_CACHE_FILE = './agent_numbers_cache.csv'
numbers_memcache = set()


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

def send_ws():
    pywhatkit.sendwhatmsg_instantly("+12345124", "Hello", tab_close=False)

def main():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, converters={'AgentNumber': str})
        df['AgentNumber'] = df['AgentNumber'].apply(clean_number)
        print(df.head())

        send_ws()
    
    else:
        print('error encountered')
        exit(1)

if __name__ == "__main__":
    args = argsparser()
    FILE, MESSAGE = args.File, args.Message
    main()