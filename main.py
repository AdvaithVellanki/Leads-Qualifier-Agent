# main.py
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr


# --- Pydantic Models for Data Contracts ---
class LeadInput(BaseModel):
    """The data model for an incoming lead from the contact form."""

    name: str
    email: EmailStr  # Pydantic validates this is a valid email format
    message: str


class LeadOutput(BaseModel):
    """The data model for the API's response after processing a lead."""

    status: str
    classification: str
    score: str
    details: str
    drafted_reply: str


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Intelligent Lead Qualifier API",
    description="An API that uses an LLM agent to classify, enrich, and score inbound leads.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "API is online and ready."}


# We will implement this endpoint in Phase 4
@app.post("/qualify-lead", response_model=LeadOutput)
async def qualify_lead(lead: LeadInput):
    """
    Receives lead data, processes it through the LangGraph agent,
    and returns the qualification results.
    """
    # Placeholder logic for now
    print(f"Received lead from: {lead.name}")

    # For now, return a dummy response that matches our LeadOutput model
    return LeadOutput(
        status="SUCCESS - DUMMY DATA",
        classification="A-Lead",
        score="95",
        details="This is a placeholder response. The agent logic is not yet implemented.",
        drafted_reply="Hello [Name], thank you for your inquiry...",
    )
