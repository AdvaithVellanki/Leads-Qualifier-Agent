# main.py
# --- Imports ---
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import operator
import json
from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from tools import get_website_title, add_lead_to_db, init_db

load_dotenv()


# --- PYDANTIC MODELS (Data Contracts) ---
class LeadInput(BaseModel):
    """The data model for an incoming lead from the contact form."""

    name: str
    email: EmailStr
    message: str


class LeadOutput(BaseModel):
    """The data model for the API's response after processing a lead."""

    status: str
    classification: str
    score: int
    company_title: str
    drafted_reply: str


# --- AGENT SETUP ---
# 1. Initialising LLM and Database
llm = ChatOllama(model="llama3:8b", temperature=0, format="json")
init_db()


# 2. Defining the Agent's State
class AgentState(TypedDict):
    """
    Represents the state of our agent. It's the memory of the workflow.
    """

    lead_input: dict
    messages: Annotated[List[BaseMessage], operator.add]
    classification: str
    company_title: str

    # Use 'Any' for score and reply initially, as they are populated later
    score: Any
    drafted_reply: Any


# 3. Define the Graph Nodes (Agent's Actions)
def classify_lead(state: AgentState) -> dict:
    """
    First node: Classifies the lead's intent based on their message.
    """
    print("---NODE: CLASSIFYING LEAD---")
    user_message = state["lead_input"]["message"]

    classification_prompt = HumanMessage(
        content=f"""
        You are a lead classification expert. Based on the user's message, classify it into ONE of the following categories:
        'sales_query', 'customer_support', 'job_application', 'spam'.

        User's message: "{user_message}"

        Return a single JSON object with one key, "classification", and the category as the value.
        """
    )

    response = llm.invoke([classification_prompt])
    result = json.loads(response.content)
    classification = result.get(
        "classification", "spam"
    )  # Default to spam if parsing fails

    print(f"Classification result: {classification}")
    return {"classification": classification}


def enrich_lead(state: AgentState) -> dict:
    """
    Node for sales queries: Enriches the lead by scraping their company website.
    """
    print("---NODE: ENRICHING LEAD---")
    lead_email = state["lead_input"]["email"]
    domain = lead_email.split("@")[1]

    title = get_website_title(domain)
    print(f"Enrichment result: {title}")

    return {"company_title": title}


def score_and_draft(state: AgentState) -> dict:
    """
    Node for sales queries: Scores the lead and drafts a personalized reply.
    """
    print("---NODE: SCORING AND DRAFTING---")
    lead_input = state["lead_input"]
    company_title = state["company_title"]

    scoring_prompt = HumanMessage(
        content=f"""
        You are a senior partner at an AI consultancy. A new lead has been enriched.
        Your task is to score this lead from 0 to 100 and draft a personalized reply.

        LEAD DETAILS:
        - Name: {lead_input["name"]}
        - Company Website Title: {company_title}
        - Message: {lead_input["message"]}

        CRITERIA:
        - High Score (80-100): Clear business need for AI services, mentions budget/timeline, from a relevant industry.
        - Medium Score (50-79): Vague business need, but seems professional.
        - Low Score (0-49): Unprofessional, spam, job-seeker, no clear need.

        RESPONSE FORMAT:
        Return a single JSON object with two keys: "score" (an integer) and "drafted_reply" (a string for the email).
        """
    )

    response = llm.invoke([scoring_prompt])
    result = json.loads(response.content)

    print(f"Scoring result: {result}")
    return {"score": result.get("score"), "drafted_reply": result.get("drafted_reply")}


# --- CONSTRUCT THE GRAPH ---

# 1. Instantiate the StateGraph with our AgentState
workflow = StateGraph(AgentState)

# 2. Add the nodes to the graph. We give each node a name.
workflow.add_node("classify_lead", classify_lead)
workflow.add_node("enrich_lead", enrich_lead)
workflow.add_node("score_and_draft", score_and_draft)


def decide_next_step(state: AgentState) -> str:
    """
    Router function that decides the next step based on the classification.
    """
    print("---ROUTER: DECIDING NEXT STEP---")
    classification = state.get("classification")

    if classification == "sales_query":
        print("Decision: Lead is a sales query. Proceeding to enrichment.")
        return "enrich_lead"
    else:
        print(f"Decision: Lead is '{classification}'. Ending process.")
        return END


# 3. Define the connections (edges) between the nodes
workflow.set_entry_point("classify_lead")

# After classification, our router function 'decide_next_step' is called.
workflow.add_conditional_edges(
    "classify_lead", decide_next_step, {"enrich_lead": "enrich_lead", END: END}
)

# After enrichment, we always proceed to scoring and drafting.
workflow.add_edge("enrich_lead", "score_and_draft")

# The scoring node is a final step in the sales path.
workflow.add_edge("score_and_draft", END)


# 4. Compile the graph into a runnable application
agent_app = workflow.compile()
print("LangGraph agent app compiled successfully.")


# --- FASTAPI APP INITIALIZATION ---
app = FastAPI(
    title="AI Lead Qualifier",
    description="An API that uses an LLM agent to classify, enrich, and score inbound leads.",
    version="0.1.0",
)


# --- API ENDPOINTS ---
@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "API is online and ready."}


@app.post("/qualify-lead", response_model=LeadOutput)
async def qualify_lead(lead: LeadInput):
    """
    Receives lead data, processes it through the LangGraph agent,
    and returns the qualification results.
    """
    print(f"\n--- NEW LEAD RECEIVED: {lead.name} ---")

    # 1. Define the initial state for the graph
    initial_state = {
        "lead_input": lead.dict(),
        "messages": [HumanMessage(content=lead.message)],
    }

    # 2. Invoke the agent app with the initial state
    final_state = agent_app.invoke(initial_state)

    # 3. Handle non-sales leads (which end early)
    if final_state.get("classification") != "sales_query":
        # We can still log them if we want
        non_sales_lead = {**final_state["lead_input"], **final_state}
        # add_lead_to_db(non_sales_lead) # Optional: decide if you want to save non-sales leads

        return LeadOutput(
            status="SUCCESS - NON-SALES LEAD",
            classification=final_state.get("classification"),
            score=0,
            company_title="N/A",
            drafted_reply="N/A - This lead was classified as non-sales and not processed further.",
        )

    # 4. Save the processed sales lead to the database
    complete_lead_data = {**final_state["lead_input"], **final_state}
    add_lead_to_db(complete_lead_data)

    # 5. Return the final, structured output
    return LeadOutput(
        status="SUCCESS - SALES LEAD PROCESSED",
        classification=final_state.get("classification"),
        score=final_state.get("score"),
        company_title=final_state.get("company_title"),
        drafted_reply=final_state.get("drafted_reply"),
    )
