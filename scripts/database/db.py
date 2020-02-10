# Database definitions

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key = True)
    fname = Column(String(100))
    lname = Column(String(100))
    rxr = Column(String(10), unique = True)
    nhs = Column(String(15))
    dob = Column(Date)
    sex = Column(String(10))

class Spirometry(Base):
    __tablename__ = 'spirometry'
    id = Column(Integer, primary_key = True)
    
    subject_id = Column(Integer, ForeignKey('patient.id'))
    subject = relationship('Patient')
  
    study_date = Column(Date)
    
    fev1_pre = Column(Float)
    fev1_pred = Column(Float)
    fev1_pre_percent_pred = Column(Float)
    fev1_pre_SR = Column(Float)

    fvc_pre = Column(Float)
    fvc_pred = Column(Float)
    fvc_pre_percent_pred = Column(Float)
    fvc_pre_SR = Column(Float)

    fev1_post = Column(Float)
    fev1_percent_change = Column(Float)
    fev1_post_percent_pred = Column(Float)
    fev1_post_SR = Column(Float)

    fvc_post = Column(Float)
    fvc_percent_change = Column(Float)
    fvc_post_percent_pred = Column(Float)
    fvc_post_SR = Column(Float)
  
class Lungfunc(Base):
    __tablename__ = 'lungfunc'
    id = Column(Integer, primary_key = True)
    
    subject_id = Column(Integer, ForeignKey('patient.id'))
    subject = relationship('Patient')
    
    spiro_id = Column(Integer, ForeignKey('spirometry.id'))
    spiro = relationship('Spirometry')

    study_date = Column(Date)

    tlco = Column(Float)
    tlco_pred = Column(Float)
    tlco_percent_pred = Column(Float)
    tlco_SR = Column(Float)
    
    vasb = Column(Float)
    vasb_pred = Column(Float)
    vasb_percent_pred = Column(Float)

    kco = Column(Float)
    kco_pred = Column(Float)
    kco_percent_pred = Column(Float)

    frc = Column(Float)
    frc_pred = Column(Float)
    frc_percent_pred = Column(Float)
    frc_SR = Column(Float)

    vc = Column(Float)
    vc_pred = Column(Float)
    vc_percent_pred = Column(Float)
    vc_SR = Column(Float)

    tlc = Column(Float)
    tlc_pred = Column(Float)
    tlc_percent_pred = Column(Float)
    tlc_SR = Column(Float)

    rv = Column(Float)
    rv_pred = Column(Float)
    rv_percent_pred = Column(Float)
    rv_SR = Column(Float)

    tlcrv = Column(Float)
    tlcrv_pred = Column(Float)
    tlcrv_percent_pred = Column(Float)
    tlcrv_SR = Column(Float)

class Physiology(Base):
    __tablename__ = 'physiology'
    id = Column(Integer, primary_key = True)

    subject_id = Column(Integer, ForeignKey('patient.id'))
    subject = relationship('Patient')

    study_date = Column(Date)
    height = Column(Float)
    weight = Column(Float)
