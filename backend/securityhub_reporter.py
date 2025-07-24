from datetime import datetime
import boto3
from excel_generator import write_excel
from utils import deduplicate_findings
import logging

def fetch_findings(start_date, end_date, creds):
    logging.info(f"📥 Fetching findings from {start_date} to {end_date} for region {creds['sso_region']}")
    if not start_date or not end_date:
        logging.error(f"Missing start_date or end_date. start_date='{start_date}', end_date='{end_date}'")
        raise ValueError("Both start_date and end_date must be provided in YYYY-MM-DD format.")

    try:
        start_time = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        end_time = datetime.strptime(end_date.strip(), "%Y-%m-%d")
    except ValueError as e:
        logging.error(f"Invalid date format. start_date='{start_date}', end_date='{end_date}'")
        raise ValueError("Invalid date format. Expected YYYY-MM-DD.") from e

    session = boto3.Session(
        aws_access_key_id=creds["access_key"],
        aws_secret_access_key=creds["secret_key"],
        aws_session_token=creds["token"],
        region_name=creds["sso_region"]
    )

    client = session.client('securityhub')

    findings = []
    paginator = client.get_paginator("get_findings")
    page_iterator = paginator.paginate(
        Filters={"CreatedAt": [{"Start": start_time.isoformat(), "End": end_time.isoformat()}]}
    )

    for page in page_iterator:
        findings.extend(page['Findings'])
        logging.info(f"🔄 Retrieved page with {len(page['Findings'])} findings")

    unique = deduplicate_findings(findings)
    logging.info(f"✅ Retrieved {len(findings)} raw findings, {len(unique)} unique findings")

    severity_order = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "INFORMATIONAL": 0
    }

    result = [{
        "resource": f["Resources"][0]["Id"],
        "title": f["Title"],
        "description": f["Description"],
        "severity": f["Severity"]["Label"],
        "created_at": f["CreatedAt"],
        "status": ""
    } for f in unique]

    result.sort(key=lambda x: severity_order.get(x["severity"].upper(), -1), reverse=True)
    return result, len(result)

def generate_securityhub_report(start_date, end_date, creds):
    data, _ = fetch_findings(start_date, end_date, creds)
    logging.info("📄 Generating Excel report for download...")
    return write_excel(data)