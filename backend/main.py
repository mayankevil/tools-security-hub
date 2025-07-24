import logging

# Configure logging to file
log_file = "../logs/securityhub.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logging.info("🚀 SecurityHub Reporter backend started")
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from securityhub_reporter import generate_securityhub_report, fetch_findings
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("../frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/findings")
def get_findings(start_date: str = Form(...), end_date: str = Form(...), sso_url: str = Form(...), sso_region: str = Form(...), access_key: str = Form(...), secret_key: str = Form(...), token: str = Form(...)):
    logging.info("[POST /findings] Request received")
    creds = {
        "sso_url": sso_url,
        "sso_region": sso_region,
        "access_key": access_key,
        "secret_key": secret_key,
        "token": token
    }
    findings, total = fetch_findings(start_date, end_date, creds)
    batch_size = 100
    batches = [findings[i:i + batch_size] for i in range(0, len(findings), batch_size)]
    return JSONResponse(content={"total": total, "batches": batches})

@app.post("/generate")
def generate_report(start_date: str = Form(...), end_date: str = Form(...), sso_url: str = Form(...), sso_region: str = Form(...), access_key: str = Form(...), secret_key: str = Form(...), token: str = Form(...)):
    logging.info("[POST /generate] Report generation triggered")
    creds = {
        "sso_url": sso_url,
        "sso_region": sso_region,
        "access_key": access_key,
        "secret_key": secret_key,
        "token": token
    }
    output_file = generate_securityhub_report(start_date, end_date, creds)
    return FileResponse(output_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=output_file)

