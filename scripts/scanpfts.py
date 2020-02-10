# Read PFT results from pdf
import sys
import os
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, folder)
#os.environ['TIKA_SERVER_JAR'] = os.path.abspath(os.path.join(folder, r'tika_java/tika-server-1.23.jar'))

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

#logging.info('Java directory: {0}'.format(os.environ['TIKA_SERVER_JAR']))

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
        if 'TREND' in str(f): continue
        parse_pdf(f, Parsetype.PT_FULL_PFT)
    for d in [x for x in p.iterdir() if x.is_dir()]:
        read_dir(d)

def parse_pdf(f: Path, p: Parsetype):
    """
    Takes a path to a pdf file and a parser to use
    Extracts data from file and adds to database
    """
    if p == Parsetype.PT_FULL_PFT:
        logging.info('Parsing {0} as PT_FULL_PFT'.format(f.name))
        result = PFTParse(f)

    else:
        logging.error('Unrecognised parser for file {0}'.format(f.name))
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
                                lname = (rec['lname'].lower().capitalize() if 'lname' in rec else None), \
                                fname = (rec['fname'].lower().capitalize() if 'fname' in rec else None), \
                                sex = (rec['sex'].lower().capitalize() if 'sex' in rec else None))
        else:
            # TODO check for inconsistencies in name & dob
            pass
        
        if 'height' in rec:
            phys = db.Physiology(subject = rxrrec, \
                                 study_date = (dtparser.parse(rec['date']).date() if 'date' in rec else None), \
                                 height = (rec['height'] if 'height' in rec else None), \
                                 weight = (rec['weight'] if 'weight' in rec else None))
            session.add(phys)
        
        if p is Parsetype.PT_FULL_PFT:
            spirorec = db.Spirometry(subject = rxrrec, \
                                     study_date = (dtparser.parse(rec['date']).date() if 'date' in rec else None))

            spirorec.fev1_pre, spirorec.fev1_pred, spirorec.fev1_pre_percent_pred, spirorec.fev1_pre_SR, \
                spirorec.fev1_post, spirorec.fev1_percent_change, spirorec.fev1_post_percent_pred, \
                spirorec.fev1_post_SR = get_spiro_vals('FEV1', rec)

            spirorec.fvc_pre, spirorec.fvc_pred, spirorec.fvc_pre_percent_pred, spirorec.fvc_pre_SR, \
                spirorec.fvc_post, spirorec.fvc_percent_change, spirorec.fvc_post_percent_pred, \
                spirorec.fvc_post_SR = get_spiro_vals('FVC', rec)

            if 'TLco' in rec:
                lungrec = db.Lungfunc(subject = rxrrec, \
                            study_date = (dtparser.parse(rec['date']).date() if 'date' in rec else None), \
                            spiro = spirorec)

                lungrec.tlco, lungrec.tlco_pred, lungrec.tlco_percent_pred, \
                    lungrec.tlco_SR = get_pft_vals('TLco', rec)
                lungrec.vasb, lungrec.vasb_pred, lungrec.vasb_percent_pred, \
                    _ = get_pft_vals('VAsb', rec)
                lungrec.kco, lungrec.kco_pred, lungrec.kco_percent_pred, \
                    _ = get_pft_vals('KCO', rec)
                lungrec.frc, lungrec.frc_pred, lungrec.frc_percent_pred, \
                    lungrec.frc_SR = get_pft_vals('FRC', rec)
                lungrec.vc, lungrec.vc_pred, lungrec.vc_percent_pred, \
                    lungrec.vc_SR = get_pft_vals('VC', rec)
                lungrec.tlc, lungrec.tlc_pred, lungrec.tlc_percent_pred, \
                    lungrec.tlc_SR = get_pft_vals('TLC', rec)
                lungrec.rv, lungrec.rv_pred, lungrec.rv_percent_pred, \
                    lungrec.rv_SR = get_pft_vals('RV', rec)
                lungrec.tlcrv, lungrec.tlcrv_pred, lungrec.tlcrv_percent_pred, \
                    lungrec.tlcrv_SR = get_pft_vals('RV_TLC', rec)

                session.add(lungrec)

            else:
                session.add(spirorec)

        
        else:
            logging.error('Problem adding record!')

        session.commit()

    else:
        logging.error('Tried to add record with no RXR')

def get_spiro_vals(key: str, rec: dict) -> tuple:
    """
    Takes a spirometry test (eg FEV1, FVC, etc) as key and returns an 8-tuple
    with pre then post measured, %predicted, SR as well as predicted and percent change
    Fills tuple position with None if value doesn't exist
    """
    if not key in rec:
        logging.error('Lung function, get_spiro_vals() - no data found')
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

def get_pft_vals(key: str, rec: dict) -> tuple:
    """
    Takes a lung function test (eg TLco, etc) as key and returns an 4-tuple
    with measured, predicted, %predicted, SR 
    Fills tuple position with None if value doesn't exist
    Use get_spiro_vals() for measures with reversibility
    """
    if not key in rec:
        logging.error('Lung function, get_pft_vals() - no data found')
        return (None, None, None, None)

    measured = (rec[key]['Measured_pre'] if 'Measured_pre' in rec[key] else None)
    pred = (rec[key]['Predicted'] if 'Predicted' in rec[key] else None)
    percent = (rec[key]['Percent_pred_pre'] if 'Percent_pred_pre' in rec[key] else None)
    sr = (rec[key]['SR_pre'] if 'SR_pre' in rec[key] else None)

    return (measured, pred, percent, sr)

if __name__ == '__main__':
    main()