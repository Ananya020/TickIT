# ==== backend/routers/chatbot.py ====
import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

# LangChain and LLM provider imports
try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_core.prompts import PromptTemplate
    from langchain_core.tools import Tool
    from langchain_openai import OpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    # Mock classes if langchain is not installed
    AgentExecutor = create_react_agent = PromptTemplate = Tool = OpenAI = ChatGoogleGenerativeAI = None
    print("Warning: 'langchain' libraries not found. Chatbot will be mocked.")

from ..database.db_connect import get_db, SessionLocal
from ..models import ticket_crud
from ..models.ticket import TicketStatus
from ..utils.logger import setup_logging
from ..dependencies import get_current_user
from ..schemas.auth import UserPayload

router = APIRouter()
logger = setup_logging()

# --- Chatbot Model and Agent Setup ---
llm = None
agent_executor = None

# --- Tool Definitions ---
# These functions allow the LangChain agent to interact with our application's data.

def get_open_tickets(priority: Optional[str] = None, category: Optional[str] = None) -> str:
    """
    Retrieves a summary of open tickets. Can be filtered by priority or category.
    Valid priorities are: Low, Medium, High, Critical.
    """
    db = SessionLocal()
    try:
        all_tickets = ticket_crud.get_all_tickets(db, limit=1000) # Get a large sample
        
        open_statuses = {TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value}
        open_tickets = [t for t in all_tickets if t.status in open_statuses]
        
        filtered_tickets = open_tickets
        if priority:
            filtered_tickets = [t for t in filtered_tickets if t.priority.lower() == priority.lower()]
        if category:
            filtered_tickets = [t for t in filtered_tickets if t.category.lower() == category.lower()]
            
        count = len(filtered_tickets)
        if count == 0:
            return "No open tickets match the specified criteria."
        
        summary = f"Found {count} open tickets matching the criteria. "
        if count <= 5:
            details = [f"Ticket ID {str(t.ticket_id)[:8]} with title '{t.title}'" for t in filtered_tickets]
            summary += "Details: " + ", ".join(details) + "."
        
        return summary
    finally:
        db.close()


def initialize_chatbot_agent():
    """Initializes the LangChain agent with tools and an LLM."""
    global llm, agent_executor
    
    if os.getenv("SKIP_AI_INIT", "false").lower() == "true":
        logger.warning("Skipping Chatbot agent initialization due to SKIP_AI_INIT=true.")
        return

    if not AgentExecutor:
        logger.error("Cannot initialize Chatbot because 'langchain' is not installed.")
        return

    # Choose LLM based on environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if openai_api_key:
        logger.info("Initializing LangChain with OpenAI LLM.")
        llm = OpenAI(temperature=0.0, openai_api_key=openai_api_key)
    elif gemini_api_key:
        logger.info("Initializing LangChain with Google Gemini LLM.")
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0, google_api_key=gemini_api_key)
    else:
        logger.warning("No OpenAI or Gemini API key found. Chatbot will use a mocked response.")
        return

    # Define the tools the agent can use
    tools = [
        Tool(
            name="get_open_tickets",
            func=get_open_tickets,
            description="Useful for finding and counting open tickets. You can filter by 'priority' or 'category'."
        ),
        # You can add more tools here to connect to other modules:
        # Tool(name="get_sla_risk", func=..., description="..."),
        # Tool(name="get_ticket_trends", func=..., description="..."),
    ]
    
    # Define the prompt template for the ReAct agent
    # This template instructs the agent on how to think and use the tools.
    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(template)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    logger.info("LangChain agent initialized successfully.")


# Initialize the agent on application startup
initialize_chatbot_agent()

# --- Pydantic Schemas for API ---
class ChatRequest(BaseModel):
    query: str = Field(..., example="How many open tickets have high priority?")

class ChatResponse(BaseModel):
    response: str

# --- API Endpoints ---
# Note: This router is mounted with prefix "/chat" in main.py.
# Expose POST "/chat" by defining path "" here.
@router.post("", response_model=ChatResponse,
             summary="Interact with the AI conversational assistant",
             response_description="The AI's response to the user's query.")
async def chat_with_assistant(
    request: ChatRequest,
    current_user: UserPayload = Depends(get_current_user)
):
    """
    Sends a query to the AI conversational assistant and receives a natural language response.

    **How it works:**
    This endpoint uses a **LangChain Agent**, which is a sophisticated LLM-powered system
    that can decide which "tools" to use to answer a question.
    1.  The user's query is passed to the agent.
    2.  The agent, guided by an LLM (OpenAI or Gemini), determines if it needs to fetch data using one of its available tools (e.g., `get_open_tickets`).
    3.  If a tool is needed, the agent calls the corresponding Python function to retrieve live data from the database.
    4.  The agent receives the data from the tool and uses the LLM to synthesize a final, human-readable answer.

    **Future Enhancements with RAG (Retrieval-Augmented Generation):**
    -   To answer more complex questions (e.g., "How do I solve VPN issues?"), this system can be enhanced with RAG.
    -   A **Vector Store** (like FAISS or a vector DB) would be created containing embeddings of all knowledge base articles, resolved ticket descriptions, and resolutions.
    -   When a user asks a question, the system would first retrieve the most relevant documents from this vector store.
    -   These retrieved documents would be passed as context to the LangChain agent, giving it the specific knowledge needed to formulate a detailed and accurate answer, significantly reducing hallucinations and improving response quality.
    """
    logger.info(f"User {current_user.email} sent query to chatbot: '{request.query}'")

    if not agent_executor:
        fallback_response = "I'm sorry, the AI assistant is not configured. Please contact an administrator."
        return ChatResponse(response=fallback_response)
        
    try:
        # Invoke the agent with the user's query
        result = agent_executor.invoke({"input": request.query})
        response_text = result.get("output", "I couldn't find a clear answer for that.")
    except Exception as e:
        logger.error(f"Error during chatbot agent execution: {e}")
        response_text = "I'm sorry, I encountered an error while processing your request. Please try again or rephrase your question."

    return ChatResponse(response=response_text)


@router.get("/health", summary="Health check for chatbot service")
async def chatbot_health():
    if os.getenv("SKIP_AI_INIT", "false").lower() == "true":
        return {"status": "ok", "agent": "skipped"}
    return {"status": "ok", "agent": bool(agent_executor)}