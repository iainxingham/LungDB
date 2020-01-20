# Read PFT results from pdf

from pathlib import Path
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import scripts.database.db as db
from parsers.parsers import Parsetype
from parsers.pft import PFTParse

import datetime as dt
from dateutil import parser as dtparser

# Set up database connection
engine = create_engine('sqlite:///.///logs///pfts.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Set up logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO, \
                    filename='./logs/lungdb.log')

def main():
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
        add_to_db(result.get_data(), p)
        
    else:
        logging.error('Failed to extract from {0}'.format(result.get_sourcefile()))     

def add_to_db(rec: dict, p: Parsetype):
    """
    Add a record to the database
    p determines type of record
    """
    if 'RXR' in rec:
        # Check if RXR in db
        rxrrec = session.query(db.Patient).filter(db.Patient.rxr == rec['RXR'].upper()).first()
        if rxrrec is None:
            # Make new rxr record
            rxrrec = db.Patient(rxr = rec['RXR'].upper(), \
                                dob = (dtparser.parse(rec['dob']).date() if 'dob' in rec else None), \
                                lname = (rec['lname'] if 'lname' in rec else None), \
                                fname = (rec['fname'] if 'fname' in rec else None))
        else:
            # TODO check for inconsistencies in name & dob
            pass
        
        if p is Parsetype.PT_FULL_PFT:
            spirorec = db.Spirometry(subject = rxrrec, \
                                     study_date = (dtparser.parse(rec['date']).date() if 'date' in rec else None))

            spirorec.fev1_pre, spirorec.fev1_pred, spirorec.fev1_pre_percent_pred, spirorec.fev1_pre_SR, \
                spirorec.fev1_post, spirorec.fev1_percent_change, spirorec.fev1_post_percent_pred, \
                spirorec.fev1_post_SR = get_pft_vals('FEV1', rec)

            spirorec.fvc_pre, spirorec.fvc_pred, spirorec.fvc_pre_percent_pred, spirorec.fvc_pre_SR, \
                spirorec.fvc_post, spirorec.fvc_percent_change, spirorec.fvc_post_percent_pred, \
                spirorec.fvc_post_SR = get_pft_vals('FVC', rec)
            
            lungrec = db.Lungfunc(subject = rxrrec, \
                                  study_date = (dtparser.parse(rec['date']).date() if 'date' in rec else None), \
                                  spiro = spirorec)
        
        else:
            logging.error('Problem adding record!')

    else:
        logging.error('Tried to add record with no RXR')

def get_pft_vals(key: str, rec: dict) -> tuple:
    """
    Takes a lung function test (eg FEV1, FVC, etc) as key and returns an 8-tuple
    with pre then post measured, %predicted, SR as well as predicted and percent change
    Fills tuple position with None if value doesn't exist
    """
    if not key in rec:
        logging.error('Lung function, get_pft_vals() - no data found')
        return (None, None, None, None, None, None, None, None)

    pre = rec[key]['Measured_pre']
    pred = rec[key]['Predicted']
    pre_percent_pred = rec[key]['Percent_pred_pre']
    pre_SR = (rec[key]['SR_pre'] if 'SR_pre' in rec[key] else None)

    post = (rec[key]['Measured_post'] if 'Measured_post' in rec[key] else None)
    post_percent_pred = (rec[key]['Percent_pred_post'] if 'Percent_pred_post' in rec[key] else None)
    percent_change = (rec[key]['Percent_change'] if 'Percent_change' in rec[key] else None)
    post_SR = (rec[key]['SR_post'] if 'SR_post' in rec[key] else None)

    return (pre, pred, pre_percent_pred, pre_SR, post, percent_change, post_percent_pred, post_SR)

if __name__ == '__main__':
    main()