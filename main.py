import os
import json
import io
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Database Setup (Cloud SQL PostgreSQL) ---
# Set DATABASE_URL in your .env or GCP Cloud Run environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    contact_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    is_admin = Column(Boolean, default=False) # Used for Admin Roles

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- App Initialization ---
app = FastAPI(title="ImageWorks Quote API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Enhanced Schema for UI Highlighting ---
class FieldSpec(BaseModel):
    value: str
    confidence: str = Field(pattern="^(High|Medium|Low)$")
    reasoning: str = Field(description="Short reason for extraction")

class DimensionValue(BaseModel):
    width: float
    height: float
    unit: str

class DimensionSpec(BaseModel):
    value: DimensionValue
    confidence: str = Field(pattern="^(High|Medium|Low)$")

class QuoteRequest(BaseModel):
    project_type: FieldSpec
    substrate: FieldSpec
    quantity: FieldSpec
    dimensions: DimensionSpec
    tolerances: FieldSpec

# --- Endpoints ---
@app.post("/api/extract-quote")
async def extract_quote(email_text: str = Form(""), files: List[UploadFile] = File(...)):
    images = []
    
    # Handle simultaneous multiple files
    for file in files:
        contents = await file.read()
        if file.content_type.startswith("image/"):
            images.append(Image.open(io.BytesIO(contents)))
        elif file.content_type.startswith("text/"):
            email_text += f"\n[Attachment: {file.filename}]\n" + contents.decode("utf-8")

    if not images and not email_text:
        raise HTTPException(status_code=400, detail="Provide text or images.")

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a manufacturing sales assistant. Analyze the email and attachments. "
            "Extract specs into the JSON schema. Provide a confidence score (High, Medium, Low) "
            "for EACH field based on clarity, and a brief reasoning."
        ),
        response_mime_type="application/json",
        response_schema=QuoteRequest,
        temperature=0.1
    )
    
    prompt = f"Customer Request:\n{email_text}\n\nExtract specs."
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt] + images, config=config)
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin Database Endpoint
@app.put("/api/admin/customers/{customer_id}")
def update_customer(customer_id: int, company_name: str, email: str, db: Session = Depends(get_db)):
    # In production, require JWT Auth here and check if current_user.is_admin is True
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    customer.company_name = company_name
    customer.email = email
    db.commit()
    return {"status": "success"}
