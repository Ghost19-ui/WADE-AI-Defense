from fastapi import APIRouter, HTTPException
from database.schemas import FeedbackRequest
from database.connection import db
import datetime

router = APIRouter()

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    if db.db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    # Save to MongoDB
    new_feedback = feedback.dict()
    new_feedback["timestamp"] = datetime.datetime.utcnow()
    
    result = await db.db["user_feedback"].insert_one(new_feedback)
    
    print(f"📝 Feedback received for {feedback.url}: {feedback.user_verdict}")
    
    return {
        "message": "Feedback received",
        "id": str(result.inserted_id)
    }