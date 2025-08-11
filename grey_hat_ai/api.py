from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import threading

# Placeholder imports: adjust if modules/classes are in submodules
try:
    from .llm_manager import LLMManager
    from .autonomous_web_agent import GreyHatAI
    from .llm_manager import LLMResponse
except ImportError:
    # fallback for direct runs
    from llm_manager import LLMManager
    from autonomous_web_agent import GreyHatAI
    from llm_manager import LLMResponse

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
    provider: str = None  # Optional, name must match LLMManager's
    model: str = None     # Optional, model name for the selected provider

class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str

class AutoTestRequest(BaseModel):
    target: str

class AutoTestResponse(BaseModel):
    queued: bool

# --- Config Endpoint ---

class ConfigRequest(BaseModel):
    provider: str
    api_key: str

class ConfigResponse(BaseModel):
    success: bool
    message: str

@app.post("/config", response_model=ConfigResponse)
async def config(request: ConfigRequest):
    """
    Configure API key for a provider.
    Ollama (local) requires no API key; only call this for remote providers.
    """
    try:
        llm_manager.set_api_key(request.provider, request.api_key)
        return {"success": True, "message": f"API key for '{request.provider}' set."}
    except Exception as e:
        return {"success": False, "message": str(e)}

# --- Models Endpoint ---

from fastapi import Query

@app.get("/models")
async def get_models(provider: str = Query(None, description="LLM provider name")):
    """
    Get available models for a given provider.
    Returns: { "models": [ ... ] }
    """
    try:
        models = llm_manager.get_available_models(provider)
    except Exception as e:
        return {"models": [], "error": str(e)}
    return {"models": models or []}

# --- Scratchpad Clear Endpoint ---

@app.post("/scratchpad/clear")
async def clear_scratchpad():
    """
    Clear all entries from the agent scratchpad.
    Returns: { "cleared": true }
    """
    scratchpad_store.clear()
    return {"cleared": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

# --- Type hints for generate_response ---
import typing

def generate_response(
    self,
    message: str,
    context: typing.List[dict]
) -> "LLMResponse":
    ...
# (Note: This is a stub; make sure LLMManager has the proper type hints in the real code.)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the assistant. Optionally specify provider/model:
    provider: one of ["ollama", "gemini", "mistral", "groq"]
    model: model id for the provider.
    Ollama (local) requires no API key; others require configuration via /config.
    """
    provider = request.provider if request.provider else getattr(llm_manager, "provider", None)
    model = request.model if request.model else getattr(llm_manager, "model", None)
    # Add minimal context, could be enhanced later
    context = []
    response = llm_manager.generate_response(request.message, context, provider, model)
    scratchpad_store.append({
        "role": "user",
        "content": request.message
    })
    scratchpad_store.append({
        "role": "assistant",
        "content": getattr(response, "content", ""),
        "provider": getattr(response, "provider", ""),
        "model": getattr(response, "model", "")
    })
    return {
        "content": getattr(response, "content", ""),
        "provider": getattr(response, "provider", ""),
        "model": getattr(response, "model", "")
    }

@app.get("/scratchpad")
async def scratchpad():
    # Returns the entire persisted scratchpad (list of exchanges)
    # Each entry is a dict: {role, content, provider?, model?}
    return {"scratchpad": scratchpad_store.get()}

@app.post("/auto-test", response_model=AutoTestResponse)
async def auto_test(request: AutoTestRequest):
    # Spawn the auto-test in a background thread
    threading.Thread(target=grey_hat_ai._start_auto_test, args=(request.target,), daemon=True).start()
    return {"queued": True}