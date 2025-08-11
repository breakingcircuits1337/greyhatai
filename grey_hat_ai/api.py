from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import threading

# Placeholder imports: adjust if modules/classes are in submodules
try:
    from .llm_manager import LLMManager
    from .autonomous_web_agent import GreyHatAI
except ImportError:
    # fallback for direct runs
    from llm_manager import LLMManager
    from autonomous_web_agent import GreyHatAI

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory scratchpad (persists for the server process lifetime)
class ScratchpadStore:
    def __init__(self):
        self._data: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def get(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._data)

    def append(self, entry: Dict[str, Any]):
        with self._lock:
            self._data.append(entry)

    def clear(self):
        with self._lock:
            self._data.clear()

scratchpad_store = ScratchpadStore()

# Initialize core components
llm_manager = LLMManager()
grey_hat_ai = GreyHatAI()

# --- Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str

class AutoTestRequest(BaseModel):
    target: str

class AutoTestResponse(BaseModel):
    queued: bool

# --- Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Call LLMManager's generate_response and log to scratchpad
    resp = llm_manager.generate_response(request.message)
    # Assume resp is a dict: { "content": ..., "provider": ..., "model": ... }
    scratchpad_store.append({
        "role": "user",
        "content": request.message
    })
    scratchpad_store.append({
        "role": "assistant",
        "content": resp.get("content", ""),
        "provider": resp.get("provider", ""),
        "model": resp.get("model", "")
    })
    return {
        "content": resp.get("content", ""),
        "provider": resp.get("provider", ""),
        "model": resp.get("model", "")
    }

@app.get("/scratchpad")
async def scratchpad():
    # Returns the entire persisted scratchpad (list of exchanges)
    return {"scratchpad": scratchpad_store.get()}

@app.post("/auto-test", response_model=AutoTestResponse)
async def auto_test(request: AutoTestRequest):
    # Enqueue auto-test using the GreyHatAI logic
    # Assumes GreyHatAI has a method _start_auto_test or similar
    # You may want to refactor this to a public method in GreyHatAI
    grey_hat_ai._start_auto_test(request.target)
    return {"queued": True}