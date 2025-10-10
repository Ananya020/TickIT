# ==== backend/routers/chatbot.py ====
import os
import random
import json
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# --- Try importing Gemini AI SDK ---
_genai_imported_successfully = True
try:
    import google.generativeai as genai
    import google.generativeai.types as genai_types
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    from google.generativeai import GenerativeModel, Content, Part
    GeminiClient = None
except ImportError:
    genai = genai_types = HarmCategory = HarmBlockThreshold = GenerativeModel = Content = Part = None
    _genai_imported_successfully = False
    GeminiClient = None

from ..database.db_connect import SessionLocal
from ..models.ticket import Ticket, TicketStatus
from ..schemas.auth import UserPayload
from ..utils.logger import setup_logging

from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
logger = setup_logging()

# --- Hardcoded Gemini API Key (for demo only) ---
GEMINI_API_KEY_HARDCODED = "AIzaSyAi1dBOdDCaicdxEh5T45-jxnJKbLcul58"

# --- Global Variables ---
genai_client = None
llm_model_instance = None
llm_model_name = "gemini-1.5-flash"
llm_available = False
gemini_tools = []


# --- Initialize Gemini ---
def initialize_chatbot_agent():
    global llm_available, genai_client, llm_model_instance, gemini_tools

    if os.getenv("SKIP_AI_INIT", "false").lower() == "true":
        logger.warning("Skipping LLM initialization due to SKIP_AI_INIT flag.")
        return

    if not _genai_imported_successfully:
        logger.warning("Gemini SDK not found. Using fallback chatbot.")
        return

    api_key_to_use = GEMINI_API_KEY_HARDCODED or os.getenv("GEMINI_API_KEY")
    if not api_key_to_use:
        logger.warning("No Gemini API key found. Using fallback chatbot.")
        return

    try:
        genai.configure(api_key=api_key_to_use)
        llm_model_instance = GenerativeModel(
            model=llm_model_name,
            safety_settings=[
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
            ]
        )
        llm_available = True
        logger.info("✅ Gemini model initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        llm_available = False

initialize_chatbot_agent()


# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    query: str = Field(..., example="How many open tickets do we have?")

class ChatResponse(BaseModel):
    response: str
    usage_metadata: Optional[Dict[str, Any]] = None


# --- Hardcoded fallback Q&A bank ---
HARDCODED_RESPONSES = {
    "hello": [
        "Hey there 👋 I’m TickIT’s AI assistant! How can I help today?",
        "Hello! Need help with tickets, SLA, or a quick issue lookup?",
        "Hi 👋 Ask me about open tickets, system status, or performance.",
        "Hey hey! Ready to tackle some IT issues together?",
    ],
    "hii": [
        "Hii! 👋 What’s up? Need help with a ticket or just checking in?",
        "Heya! How’s your day going?",
        "Hii there — glad to see you back!",
        "Hey! 😊 How can I help today?",
    ],
    "hi": [
        "Hi there! How can I make your day easier?",
        "Hey 👋 Need help with something specific?",
        "Hi hi! Always ready to chat about tickets or systems!",
    ],
    "good morning": [
        "Good morning ☀️ Hope your day starts off smooth!",
        "Morning! Let’s make those tickets disappear one by one 😄",
        "Good morning! Coffee + clean dashboards — the perfect combo.",
    ],
    "good afternoon": [
        "Good afternoon 🌞 Need a quick update on system status?",
        "Afternoon! Still keeping up with SLAs, I hope 😉",
        "Hey! Afternoon check-in — all systems stable here.",
    ],
    "good evening": [
        "Good evening 🌙 Wrapping up your tickets for the day?",
        "Evening! Let’s get a few more issues resolved before calling it a night!",
        "Good evening! Time to check what’s pending for tomorrow?",
    ],
    "bye": [
        "Goodbye! Have a great day 👋",
        "Bye! Don’t forget to close resolved tickets.",
        "See you later — stay productive!",
        "Catch you later! I’ll keep things running here 🤖",
    ],
    "thank you": [
        "You're welcome 😊",
        "Glad to help!",
        "Anytime! Happy to assist.",
        "No problem! That’s what I’m here for 😄",
    ],
    "thanks": [
        "No worries! Always happy to help.",
        "You got it 👍",
        "My pleasure!",
        "Anytime — that’s my job 😎",
    ],
    "how are you": [
        "I’m running perfectly, thanks for asking 😄",
        "All systems operational — feeling great!",
        "I’m good! Monitoring tickets and sipping on virtual coffee ☕",
    ],
    "who are you": [
        "I’m TickIT 🤖, your IT helpdesk assistant.",
        "I’m an AI assistant here to manage tickets and answer your questions.",
        "TickIT at your service! Here to make your support work easier.",
    ],
    "what can you do": [
        "I can show ticket metrics, SLA health, and even recommend resolutions.",
        "I help with tickets — creating, checking status, or finding solutions.",
        "I track tickets, system health, and team performance!",
    ],
    "what's up": [
        "Just doing my rounds through the ticket database 😎",
        "Same old — keeping systems happy!",
        "Monitoring performance metrics as usual 👀",
    ],

    # ==== TICKET METRICS ====
    "open tickets": [
        "There are currently 12 open tickets — 5 high, 4 medium, and 3 low priority.",
        "We have 12 open tickets. Most are related to VPN issues and printer errors.",
        "Total open tickets: 12. High priority: 5, Medium: 4, Low: 3.",
        "12 tickets are still open, but progress looks steady.",
    ],
    "resolved today": [
        "7 tickets resolved today, mainly VPN and login-related.",
        "8 tickets were closed today — performance up 12%.",
        "Resolved tickets today: 7. Mostly software errors.",
        "Looks like your team’s on fire 🔥 — 7 issues fixed today!",
    ],
    "high priority": [
        "There are 5 high-priority tickets pending, mostly network-related.",
        "Currently 5 high-priority tickets open. 3 are nearing SLA limits.",
        "5 critical issues pending — network and software primarily.",
        "We’ve got 5 urgent tickets to tackle today. Let’s go 💪",
    ],
    "team performance": [
        "SLA compliance: 92%. Avg resolution time: 6.8 hours.",
        "Agent productivity rose by 14%. Avg closure: 7 hrs per ticket.",
        "Team performance is solid. Ananya leads with fastest response time!",
        "Your team’s trending well — fast closures and healthy SLA stats!",
    ],
    "sla": [
        "Current SLA compliance is 92%. Two high-priority tickets are nearing breach.",
        "SLA health looks good — only 2% tickets risk breaching deadlines.",
        "All SLAs are green except two that are about to expire soon.",
        "You’re in good shape — SLA compliance above 90%!",
    ],

    # ==== ISSUE-SPECIFIC RESPONSES ====
    "vpn": [
        "For VPN issues, restart the VPN client or update your network drivers.",
        "VPN not connecting? Try re-authenticating or checking your firewall settings.",
        "Common VPN fixes: Restart client, flush DNS, or update credentials.",
        "Try disconnecting and reconnecting VPN — works 90% of the time 😉",
    ],
    "printer": [
        "Check if the printer is online and restart the spooler service.",
        "Reinstalling the printer drivers often resolves this issue.",
        "Ensure the printer is shared correctly and powered on.",
        "Have you tried turning it off and on again? Works wonders for printers 😅",
    ],
    "slow system": [
        "Try closing background apps and cleaning temp files.",
        "Clearing cache and disabling startup apps often helps.",
        "Run a system cleanup — usually fixes laggy performance.",
        "Maybe too many browser tabs? 😏 Close a few and check again.",
    ],
    "password reset": [
        "Go to the company portal → Forgot Password → Verify via email or SMS.",
        "Use the ‘Forgot Password’ option on the login page.",
        "Head to the portal and verify with your email for a quick reset.",
        "If you’re locked out, your IT admin can force-reset it too.",
    ],
    "network": [
        "Reconnect to Wi-Fi or restart your router. Check VPN settings if remote.",
        "Network drops? Try renewing your IP or resetting your adapter.",
        "Most network issues resolve with a router restart or DNS flush.",
        "If it’s still unstable, test with a wired connection temporarily.",
    ],
    "security": [
        "Security tickets are handled by InfoSec. Last incident was a phishing email.",
        "Our security system detected 3 phishing attempts this week.",
        "Security alerts are under control — no major breaches detected.",
        "Everything’s locked down 🔐 No current threats.",
    ],

    # ==== AI / SYSTEM STATUS ====
    "ai classify": [
        "The AI model classifies issues into Hardware, Software, Network, or Security categories.",
        "Auto-classification uses NLP to understand ticket descriptions.",
        "Our classifier achieves 94% accuracy in identifying ticket categories.",
        "AI sorting ensures faster routing of issues to the right agents.",
    ],
    "recommend resolution": [
        "Top fixes: Restart service, apply patch, and clear cache.",
        "Based on history, common fixes are: reboot, update, reconfigure.",
        "Resolutions include: Check configs, restart affected service, reinstall dependencies.",
        "I can suggest solutions based on ticket patterns — want me to try?",
    ],
    "escalate": [
        "Tickets unresolved for 4+ hours auto-escalate to higher tiers.",
        "Escalation policy triggers after SLA breach thresholds.",
        "Critical issues are immediately escalated to Level 3 engineers.",
        "Escalation ensures critical cases get attention fast 🚨",
    ],
    "status": [
        "All systems operational. Minor delay reported on the database server.",
        "Servers are up and running. Average response time: 0.8 seconds.",
        "System health check: ✅ No major issues detected.",
        "Everything’s green — uptime steady at 99.99%.",
    ],

    # ==== HELP & RANDOM CHAT ====
    "help": [
        "You can ask things like:\n• Show open tickets\n• SLA breach risk\n• Fix for VPN issue\n• Team performance",
        "Try asking:\n- 'How many tickets are open?'\n- 'Any SLA breaches?'\n- 'Show team metrics.'",
        "Here are sample queries:\n'VPN not working', 'System status', 'AI classify ticket'.",
        "Need ideas? Try 'show recent tickets' or 'who resolved most today'.",
    ],
    "joke": [
        "Why did the server go to therapy? Too many connections 😂",
        "I told a joke about UDP… but I’m not sure if you got it.",
        "Why did the laptop stay home? It had a hard drive 😜",
    ],
    "good night": [
        "Good night 🌙 Don’t forget to log off!",
        "Sleep well! I’ll keep an eye on tickets while you rest.",
        "Sweet dreams! No alerts on the radar tonight 🌌",
    ],
    "good job": [
        "Aww, thanks! You’re doing great too 😄",
        "Appreciate it! Always here to help.",
        "Teamwork makes the dream work 💪",
    ],
    "love you": [
        "Aww 🥺 you’re too kind!",
        "I’d blush if I could 😳",
        "Haha thanks! I’m just here to make your life easier 💙",
    ],
    "open tickets": [
        "There are currently 12 open tickets — 5 high, 4 medium, and 3 low priority.",
        "We have 12 open tickets. Most are related to VPN issues and printer errors.",
        "Total open tickets: 12. High priority: 5, Medium: 4, Low: 3."
    ],
    "vpn": [
        "For VPN issues, restart the VPN client or update your network drivers.",
        "VPN not connecting? Try re-authenticating or checking your firewall settings.",
        "Common VPN fixes: Restart client, flush DNS, or update credentials."
    ],
    "printer": [
        "Check if the printer is online and restart the spooler service.",
        "Reinstalling the printer drivers often resolves this issue.",
        "Ensure the printer is shared correctly and powered on."
    ],
    "slow system": [
        "Try closing background apps and cleaning temp files. Performance improves significantly.",
        "Clearing cache and disabling startup apps often fixes slow performance.",
        "Run a quick system cleanup — this usually helps with slowdowns."
    ],
    "password reset": [
        "Go to the company portal → Forgot Password → Verify via email or SMS.",
        "Use the ‘Forgot Password’ option on the login page. You’ll get a reset link.",
        "Password resets are easy — head to the portal and verify with your email."
    ],
    "network": [
        "Reconnect to Wi-Fi or restart your router. Check VPN settings if remote.",
        "Network drops? Try renewing your IP or resetting your network adapter.",
        "Most network issues resolve with a router restart or DNS flush."
    ],
    "security": [
        "Security tickets are handled by InfoSec. Last incident was a phishing email.",
        "Our security system detected 3 phishing attempts this week.",
        "Security alerts are under control — no major breaches detected."
    ],
    "sla": [
        "Current SLA compliance is 92%. Two high-priority tickets are nearing breach.",
        "SLA health looks good — only 2% tickets risk breaching deadlines.",
        "All SLAs are green except two that are about to expire soon."
    ],
    "status": [
        "All systems operational. Minor delay reported on the database server.",
        "Servers are up and running. Average response time: 0.8 seconds.",
        "System health check: ✅ No major issues detected."
    ],
    "ai classify": [
        "The AI model classifies issues into Hardware, Software, Network, or Security categories.",
        "Auto-classification uses NLP to understand ticket descriptions.",
        "Our classifier achieves 94% accuracy in identifying ticket categories."
    ],
    "recommend resolution": [
        "Top fixes: Restart service, apply patch, and clear cache.",
        "Based on history, 3 most common fixes are: reboot, update, reconfigure.",
        "Resolutions include: Check configs, restart affected service, reinstall dependencies."
    ],
    "escalate": [
        "Tickets unresolved for 4+ hours auto-escalate to higher support tiers.",
        "Escalation policy triggers after SLA breach thresholds.",
        "Critical issues are immediately escalated to Level 3 engineers."
    ],
    "hello": [
        "Hey there 👋 I’m TickIT’s AI assistant! How can I help today?",
        "Hello! Need help with tickets, SLA, or a quick issue lookup?",
        "Hi 👋 Ask me about open tickets, system status, or performance."
    ],
    "help": [
        "You can ask things like:\n• Show open tickets\n• SLA breach risk\n• Fix for VPN issue\n• Team performance",
        "Try asking:\n- 'How many tickets are open?'\n- 'Any SLA breaches?'\n- 'Show team metrics.'",
        "Here are sample queries:\n'VPN not working', 'System status', 'AI classify ticket'."
    ],
    "high priority": [
        "There are 5 high-priority tickets pending, mostly network-related.",
        "Currently 5 high-priority tickets open. 3 are nearing SLA limits.",
        "5 critical issues pending — network and software primarily."
    ],
    "resolved today": [
        "7 tickets resolved today, mainly VPN and login-related.",
        "8 tickets were closed today — performance up 12%.",
        "Resolved tickets today: 7. Mostly software errors."
    ],
    "team performance": [
        "SLA compliance: 92%. Avg resolution time: 6.8 hours.",
        "Agent productivity rose by 14%. Avg closure: 7 hrs per ticket.",
        "Team performance is solid. Ananya leads with fastest response time!"
    ],
    "thank you": [
        "You're welcome 😊",
        "Glad to help!",
        "Anytime! Happy to assist."
    ],
    "bye": [
        "Goodbye! Have a great day 👋",
        "Bye! Don’t forget to close resolved tickets.",
        "See you later — stay productive!"
    ]
}


# --- Hybrid Chat Endpoint ---
@router.post("", response_model=ChatResponse)
async def chat_with_assistant(
    request: Optional[ChatRequest] = None,
    query: Optional[str] = None
):
    effective_query = (request.query if request else None) or (query or "").strip()
    if not effective_query:
        raise HTTPException(status_code=422, detail="Query is required")

    q = effective_query.lower()

    # --- Try Gemini if available ---
    if llm_available and llm_model_instance:
        try:
            logger.info("Attempting Gemini response...")
            response = llm_model_instance.generate_content(
                contents=[genai_types.to_content(effective_query)],
                generation_config=genai_types.GenerateContentConfig(temperature=0.3)
            )
            if response.candidates and response.candidates[0].content.text:
                return ChatResponse(
                    response=response.candidates[0].content.text,
                    usage_metadata={"model": llm_model_name, "type": "Gemini-Online"}
                )
        except Exception as e:
            logger.error(f"Gemini error: {e}. Switching to fallback mode.")

    # --- Fallback: hardcoded responses ---
    for keyword, options in HARDCODED_RESPONSES.items():
        if keyword in q:
            return ChatResponse(
                response=random.choice(options),
                usage_metadata={"model": "TickIT-MVP", "type": "Hardcoded"}
            )

    # --- Default unknown response ---
    return ChatResponse(
        response=(
            "Hmm, I'm not sure about that. Try asking about open tickets, SLA status, "
            "VPN issues, or performance metrics."
        ),
        usage_metadata={"model": "TickIT-MVP", "type": "Fallback-Generic"}
    )


# --- Health Check Endpoint ---
@router.get("/health")
async def chatbot_health():
    return {
        "status": "ok" if llm_available else "fallback",
        "model_name": llm_model_name,
        "provider": "Gemini" if llm_available else "Offline",
        "hardcoded_mode": not llm_available
    }
