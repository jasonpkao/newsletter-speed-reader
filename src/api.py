import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from crews.newsletter_crew import analyze_email_content

load_dotenv()

app = FastAPI(title="Newsletter Summarizer API")


class EmailInput(BaseModel):
    subject: str
    sender: str
    date: Optional[str] = ""
    body: str
    url: Optional[str] = ""


class SummaryOutput(BaseModel):
    title: str
    source: str
    date: str
    topics: List[str]
    summary: str
    url: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/summarize", response_model=SummaryOutput)
def summarize(email: EmailInput):
    try:
        result = analyze_email_content(
            subject=email.subject,
            sender=email.sender,
            date=email.date or "",
            body=email.body,
        )
        if not result.get("url"):
            result["url"] = email.url or ""
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
