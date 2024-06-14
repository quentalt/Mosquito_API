from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
class MosquitoReport(Base):
    __tablename__ = 'mosquito_reports'

    id = Column(None, Integer(), primary_key=True, nullable=False)
    location = Column(String, index=True)
    species = Column(String, index=True)
    date = Column(DateTime, index=True)
    observations = Column(String, nullable=True)
    disease = Column(String)
    number = Column(Integer)

class Traitement(Base):
    __tablename__ = 'traitements'

    id = Column(None, Integer(), primary_key=True, nullable=False)
    description = Column(String)
    maladie_id = Column(Integer, ForeignKey('maladies.id'))

    maladie = relationship("Maladie", back_populates="traitements")

class Maladie(Base):
    __tablename__ = 'maladies'

    id = Column(None, Integer(), primary_key=True, nullable=False)
    nom = Column(String, index=True)

    traitements = relationship("Traitement", back_populates="maladie")

class Contamination(Base):
    __tablename__ = 'contaminations'

    id = Column(None, Integer(), primary_key=True, nullable=False)
    species = Column(String, index=True)
    total_tested = Column(Integer)
    total_contaminated = Column(Integer)
    contamination_rate = Column(Float)
    location = Column(String, index=True)
    date = Column(DateTime, index=True)