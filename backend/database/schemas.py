from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    url: str
    html_content: Optional[str] = None
    scripts: Optional[str] = None      
    screenshot: Optional[str] = None

class FeedbackRequest(BaseModel):
    url: str
    risk_score: float
    user_verdict: str = Field(..., pattern="^(safe|phishing)$")

class ScanResult(BaseModel):
    url: str
    risk_score: float
    verdict: str
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    features: Optional[dict] = {}

class UserFeedback(BaseModel):
    url: str
    risk_score: float
    user_verdict: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)