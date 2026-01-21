import os
import sqlite3
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="Fashion & Beauty REST API",
    description="""
REST API za pristup integriranim podacima o modnim i beauty proizvodima.

Podaci:
- Kaggle Fashion Product Images dataset (modni proizvodi)
- DummyJSON REST API (cijene i korisničke ocjene)
- Integracija po kategorijama
- Pohrana u SQLite bazu podataka
""",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(__file__)  
DB_PATH = os.path.join(BASE_DIR, "instance", "fashion.db")  

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class CategoryStats(BaseModel):
    masterCategory: str
    kaggle_count: int
    mappedCategory: str
    avg_price: float
    avg_rating: float
    dummy_count: int

@app.get("/", response_class=HTMLResponse, summary="Web stranica (analiza + grafovi)")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/categories", response_model=List[CategoryStats], summary="Dohvat statistike po kategorijama")
def get_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM category_stats")
    rows = cursor.fetchall()
    columns = [c[0] for c in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]
