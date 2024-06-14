from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from config import Settings
from models import MosquitoReport as MosquitoReportModel
from models import Traitement, Maladie, Contamination

import os

app = FastAPI()

load_dotenv()


DB_URL = os.getenv("DB_URL")
DEBUG = os.getenv("DEBUG") == "True"


class MosquitoReport(BaseModel):
    id: int
    location: str
    species: str
    date: datetime
    observations: str | None
    disease: str
    number: int

    class Config:
        from_attributes = True

class TraitementSchema(BaseModel):
    id: int
    description: str
    maladie_id: int

    class Config:
        from_attributes = True

class MaladieSchema(BaseModel):
    id: int
    nom: str
    traitements: list[TraitementSchema] = []

    class Config:
        from_attributes = True

class ContaminationRate(BaseModel):
    id: int
    species: str
    total_tested: int
    total_contaminated: int
    contamination_rate: float
    location: str
    date: datetime


    class Config:
        from_attributes = True

settings = Settings()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
@app.get("/config/")
@app.get("/config/")
def read_config():
    return {"DB_URL": settings.DB_URL, "Debug Mode": settings.DEBUG}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mosquito API"}

@app.post("/mosquito/", response_model=MosquitoReport)
def create_mosquito_report(mosquito: MosquitoReport, db: Session = Depends(get_db)):
    db_mosquito = MosquitoReportModel(**mosquito.dict())
    db.add(db_mosquito)
    db.commit()
    db.refresh(db_mosquito)
    return db_mosquito

@app.get("/mosquito/{mosquito_id}", response_model=MosquitoReport)
def read_mosquito_report(mosquito_id: int, db: Session = Depends(get_db)):
    db_mosquito = db.query(MosquitoReportModel).filter(MosquitoReportModel.id == mosquito_id).first()
    if db_mosquito is None:
        raise HTTPException(status_code=404, detail="Mosquito not found")
    return db_mosquito

@app.put("/mosquito/{mosquito_id}", response_model=MosquitoReport)
def update_mosquito_report(mosquito_id: int, mosquito: MosquitoReport, db: Session = Depends(get_db)):
    db_mosquito = db.query(MosquitoReportModel).filter(MosquitoReportModel.id == mosquito_id).first()
    if db_mosquito is None:
        raise HTTPException(status_code=404, detail="Mosquito not found")
    for key, value in mosquito.dict().items():
        setattr(db_mosquito, key, value)
    db.commit()
    db.refresh(db_mosquito)
    return db_mosquito

@app.delete("/mosquito/{mosquito_id}", response_model=MosquitoReport)
def delete_mosquito_report(mosquito_id: int, db: Session = Depends(get_db)):
    db_mosquito = db.query(MosquitoReportModel).filter(MosquitoReportModel.id == mosquito_id).first()
    if db_mosquito is None:
        raise HTTPException(status_code=404, detail="Mosquito not found")
    db.delete(db_mosquito)
    db.commit()
    return db_mosquito

@app.get("/mosquito/species/{species}", response_model=List[MosquitoReport])
def read_mosquito_reports_by_species(species: str, db: Session = Depends(get_db)):
    return db.query(MosquitoReportModel).filter(MosquitoReportModel.species == species).all()

@app.get("/mosquito/date/{date}", response_model=List[MosquitoReport])
def read_mosquito_reports_by_date(date: datetime, db: Session = Depends(get_db)):
    return db.query(MosquitoReportModel).filter(MosquitoReportModel.date == date).all()

@app.get("/mosquito/location/{location}", response_model=MosquitoReport)
def read_last_mosquito_report_by_location(location: str, db: Session = Depends(get_db)):
    return db.query(MosquitoReportModel).filter(MosquitoReportModel.location == location).order_by(
        MosquitoReportModel.date.desc()).first()

@app.get("/mosquito/last/", response_model=MosquitoReport)
def read_last_mosquito_report(db: Session = Depends(get_db)):
    return db.query(MosquitoReportModel).order_by(MosquitoReportModel.date.desc()).first()

@app.get("/contamination/", response_model=List[ContaminationRate])
def read_contamination_rates(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Contamination).offset(skip).limit(limit).all()

@app.post("/contamination/", response_model=ContaminationRate)
def create_contamination_rate(contamination: ContaminationRate, db: Session = Depends(get_db)):
    db_contamination = Contamination(**contamination.dict())
    db.add(db_contamination)
    db.commit()
    db.refresh(db_contamination)
    return db_contamination

@app.get("/contamination/{contamination_id}", response_model=ContaminationRate)
def read_contamination_rate(contamination_id: int, db: Session = Depends(get_db)):
    db_contamination = db.query(Contamination).filter(Contamination.id == contamination_id).first()
    if db_contamination is None:
        raise HTTPException(status_code=404, detail="Contamination rate not found")
    return db_contamination

@app.get("/contamination/species/{species}", response_model=List[ContaminationRate])
def read_contamination_rates_by_species(species: str, db: Session = Depends(get_db)):
    return db.query(Contamination).filter(Contamination.species == species).all()

@app.get("/contamination/location/{location}", response_model=List[ContaminationRate])
def read_contamination_rates_by_location(location: str, db: Session = Depends(get_db)):
    return db.query(Contamination).filter(Contamination.location == location).all()

@app.post("/traitement/", response_model=TraitementSchema)
def create_traitement(traitement: TraitementSchema, db: Session = Depends(get_db)):
    db_traitement = Traitement(**traitement.dict())
    db.add(db_traitement)
    db.commit()
    db.refresh(db_traitement)
    return db_traitement

@app.get("/traitement/{traitement_id}", response_model=TraitementSchema)
def read_traitement(traitement_id: int, db: Session = Depends(get_db)):
    db_traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
    if db_traitement is None:
        raise HTTPException(status_code=404, detail="Traitement not found")
    return db_traitement

@app.get("/traitement/maladie/{maladie_id}", response_model=MaladieSchema)
def read_traitement_by_maladie(maladie_id: int, db: Session = Depends(get_db)):
    db_maladie = db.query(Maladie).filter(Maladie.id == maladie_id).first()
    if db_maladie is None:
        raise HTTPException(status_code=404, detail="Maladie not found")
    return db_maladie

@app.post("/maladie/", response_model=MaladieSchema)
def create_maladie(maladie: MaladieSchema, db: Session = Depends(get_db)):
    db_maladie = Maladie(**maladie.dict())
    db.add(db_maladie)
    db.commit()
    db.refresh(db_maladie)
    return db_maladie

@app.get("/maladie/{maladie_id}", response_model=MaladieSchema)
def read_maladie(maladie_id: int, db: Session = Depends(get_db)):
    db_maladie = db.query(Maladie).filter(Maladie.id == maladie_id).first()
    if db_maladie is None:
        raise HTTPException(status_code=404, detail="Maladie not found")
    return db_maladie

@app.get("/maladie/nom/{nom}", response_model=MaladieSchema)
def read_maladie_by_nom(nom: str, db: Session = Depends(get_db)):
    db_maladie = db.query(Maladie).filter(Maladie.nom == nom).first()
    if db_maladie is None:
        raise HTTPException(status_code=404, detail="Maladie not found")
    return db_maladie