import os
import json
import shutil
import zipfile
import logging
from typing import List, Optional
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import Contact, ExtractResponse, SendMessageRequest, DeliveryReport
from app.pdf_extractor import extract_contacts_from_pdf
from app.sms_sender import send_bulk
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

# Directory Setup
UPLOAD_DIR = settings.UPLOAD_DIR
OUTPUT_DIR = settings.OUTPUT_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount Static Files and Templates
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates" if os.path.exists("templates") else ".")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renders main dashboard UI.
    """
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})

@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    """
    Accepts ZIP file upload, extracts PDFs to /tmp/pdfs/, and returns PDF file list.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a ZIP archive")

    # Clear previous upload directory
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    zip_path = os.path.join(OUTPUT_DIR, "uploaded.zip")
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(UPLOAD_DIR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract ZIP archive: {str(e)}")

    # Gather extracted PDF files
    extracted_pdfs = []
    for root, _, files in os.walk(UPLOAD_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                extracted_pdfs.append(os.path.relpath(os.path.join(root, f), UPLOAD_DIR))

    return {
        "status": "success",
        "message": f"Successfully extracted {len(extracted_pdfs)} PDF files",
        "count": len(extracted_pdfs),
        "pdf_files": extracted_pdfs
    }

@app.post("/extract-contacts", response_model=ExtractResponse)
async def extract_contacts():
    """
    Parses all extracted PDFs in /tmp/pdfs/, runs regex and OCR fallback extraction,
    deduplicates contacts, saves contacts.json and all_contacts.csv, and returns contacts list.
    """
    pdf_files = []
    for root, _, files in os.walk(UPLOAD_DIR):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files found in upload directory. Please upload a ZIP file first.")

    all_contacts: List[Contact] = []
    seen_phones = set()

    for pdf_path in pdf_files:
        contacts = extract_contacts_from_pdf(pdf_path)
        for contact in contacts:
            if contact.phone not in seen_phones:
                seen_phones.add(contact.phone)
                all_contacts.append(contact)

    # Save to json and csv
    json_path = os.path.join(OUTPUT_DIR, "contacts.json")
    csv_path = os.path.join(OUTPUT_DIR, "all_contacts.csv")

    contacts_data = [c.model_dump() for c in all_contacts]
    with open(json_path, "w") as f:
        json.dump(contacts_data, f, indent=2)

    df = pd.DataFrame(contacts_data)
    df.to_csv(csv_path, index=False)

    return ExtractResponse(
        status="success",
        pdf_count=len(pdf_files),
        total_contacts=len(all_contacts),
        contacts=all_contacts
    )

@app.post("/send-messages", response_model=DeliveryReport)
async def send_messages(req: SendMessageRequest):
    """
    Executes bulk message delivery for provided contacts list using specified channel.
    Renders {{name}} and {{phone}} template variables.
    """
    if not req.contacts:
        raise HTTPException(status_code=400, detail="Contacts list cannot be empty.")

    config = {
        "fast2sms_api_key": req.fast2sms_api_key,
        "twilio_sid": req.twilio_sid,
        "twilio_token": req.twilio_token,
        "twilio_whatsapp_from": req.twilio_whatsapp_from,
        "telegram_bot_token": req.telegram_bot_token
    }

    report = send_bulk(
        contacts=req.contacts,
        template_msg=req.message,
        channel=req.channel.lower(),
        config=config
    )

    # Save delivery report
    report_csv = os.path.join(OUTPUT_DIR, "delivery_report.csv")
    report_excel = os.path.join(OUTPUT_DIR, "delivery_report.xlsx")

    results_data = [res.model_dump() for res in report.results]
    df = pd.DataFrame(results_data)
    df.to_csv(report_csv, index=False)
    df.to_excel(report_excel, index=False)

    return report

@app.get("/report")
async def get_report(format: str = Query("csv", regex="^(csv|excel)$")):
    """
    Downloads delivery report in CSV or Excel format.
    """
    if format == "csv":
        filepath = os.path.join(OUTPUT_DIR, "delivery_report.csv")
        media_type = "text/csv"
        filename = "delivery_report.csv"
    else:
        filepath = os.path.join(OUTPUT_DIR, "delivery_report.xlsx")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "delivery_report.xlsx"

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found. Please run message dispatch first.")

    return FileResponse(path=filepath, filename=filename, media_type=media_type)
