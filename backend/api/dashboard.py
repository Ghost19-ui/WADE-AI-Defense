from fastapi import APIRouter
from database.connection import db
from typing import List, Dict

router = APIRouter()

@router.get("/dashboard/stats")
async def get_stats():
    if db.db is None:
        return {"error": "Database not connected"}

    total_scans = await db.db["scan_history"].count_documents({})
    phishing_count = await db.db["scan_history"].count_documents({"verdict": "Phishing"})
    safe_count = await db.db["scan_history"].count_documents({"verdict": "Safe"})
    
    return {
        "total_scans": total_scans,
        "phishing": phishing_count,
        "safe": safe_count,
        "suspicious": total_scans - (phishing_count + safe_count)
    }

@router.get("/dashboard/recent")
async def get_recent_scans():
    if db.db is None:
        return []

    cursor = db.db["scan_history"].find().sort("timestamp", -1).limit(10)
    scans = await cursor.to_list(length=10)

    for scan in scans:
        scan["_id"] = str(scan["_id"])
    
    return scans