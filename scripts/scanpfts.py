# Read PFT results from pdf

from pathlib import Path
import logging

from parsers.parsers import Parsetype
from parsers.pft import PFTParse

def main():
    # Set up logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO, \
                        filename='./logs/lungdb.log')    

    # Main work of programme
    logging.info('Starting main - scanpfts.py')
    p = Path('./data') # Replace this with pft directory
    read_dir(p)

def read_dir(p: Path):
    """
    Recursively read through a directory and subdirectories
    For each pdf file found, extract PFT results by calling parse_pdf()
    """
    logging.info('Reading {0}'.format(p.name))
    for f in p.glob('*.pdf'):
        parse_pdf(f.name, Parsetype.PT_FULL_PFT)
    for d in [x for x in p.iterdir() if x.is_dir()]:
        read_dir(d)

def parse_pdf(f: Path, p: Parsetype):
    """
    Takes a path to a pdf file and a parser to use
    Extracts data from file and adds to database
    """
    if p == Parsetype.PT_FULL_PFT:
        logging.info('Parsing {0} as PT_FULL_PFT'.format(p.name))
        result = PFTParse(f)

    else:
        logging.error('Unrecognised parser for file {0}'.format(p.name))
        return

    if result.is_ok():
        result.get_data()
        # Add to database here
    else:
        logging.error('Failed to extract from {0}'.format(result.get_sourcefile()))     


if __name__ == '__main__':
    main()