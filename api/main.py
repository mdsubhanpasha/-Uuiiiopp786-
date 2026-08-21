from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import PyPDF2
import io
import time

from . import models, database, rag

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TestGen AI Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    id: int
    text: str
    citation: str

class UploadResponse(BaseModel):
    status: str
    message: str
    questions: list[Question]

@app.get("/")
def read_root():
    return {"message": "TestGen AI Pro API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        time.sleep(1)
        questions = rag.process_document(text)

        return {
            "status": "success",
            "message": "Questions generated successfully",
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
