from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import threading
import time
from fastapi import HTTPException

# Placeholder imports: adjust if modules/classes are in submodules
try:
    from .llm_manager import LLMManager
    from .autonomous_web_agent import GreyHatAI
    from .llm_manager import LLMResponse
    from .voice_engine import VoiceEngine, VoiceConfig
except ImportError:
    # fallback for direct runs
    from llm_manager import LLMManager
    from autonomous_web_agent import GreyHatAI
    from llm_manager import LLMResponse
    from voice_engine import VoiceEngine, VoiceConfig

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
voice_engine = VoiceEngine(VoiceConfig())

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

# --- Voice Endpoints ---

from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import status

@app.get("/voice/voices")
async def get_voices():
    """
    Get available voices.
    Returns: { "voices": { voice_id: name, ... } }
    """
    try:
        voices = voice_engine.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    voice_id: str = None
    provider: str = None  # "elevenlabs" or "piper"

@app.post("/voice/tts")
async def voice_tts(req: TTSRequest):
    """
    Text-to-speech endpoint. Returns audio/wav stream.
    Optional: provider ("elevenlabs" or "piper")
    """
    try:
        audio_bytes = voice_engine.text_to_speech(req.text, req.voice_id, req.provider)
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=output.wav"}
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

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

# --- In-memory auto-test report store ---
auto_test_reports = {}  # target -> report data (dict)
auto_test_locks = {}    # target -> threading.Lock

def _generate_sample_report(target):
    # In real usage, call grey_hat_ai._start_auto_test(target) and parse results
    # Here, simulate with a dummy structure and a mermaid diagram
    return {
        "target": target,
        "summary": "Automated security assessment completed.",
        "reconnaissance": {
            "diagram": f"""
graph TD
    A[User Machine] -->|Scan| B({target})
    B --> C[Web Server]
    B --> D[SSH Service]
    C --> E[Vulnerability: XSS]
    D --> F[Vulnerability: Weak SSH Key]
""",
            "findings": [
                "Open ports: 22, 80, 443",
                "Detected web server: nginx 1.18",
                "SSH service running",
            ]
        },
        "vulnerabilities": [
            {"id": "CVE-2023-1234", "desc": "Remote code execution in nginx", "severity": "high"},
            {"id": "MISCONFIG-SSH", "desc": "Weak SSH key detected", "severity": "medium"}
        ],
        "exploitation": {
            "plan": [
                "Exploit XSS on web server to gain session cookie",
                "Use weak SSH key for lateral movement"
            ]
        }
    }

def run_auto_test_and_store(target):
    # Simulate a long-running test
    time.sleep(4)  # Emulate test duration
    report = _generate_sample_report(target)
    auto_test_reports[target] = report

@app.post("/auto-test", response_model=AutoTestResponse)
async def auto_test(request: AutoTestRequest):
    """
    Start an auto-test for the given target. Returns queued=True immediately,
    and the result will be available via /auto-test/results?target=
    """
    target = request.target
    # Avoid parallel runs for same target
    if target in auto_test_locks:
        raise HTTPException(status_code=409, detail="Test already running for this target")
    lock = threading.Lock()
    auto_test_locks[target] = lock
    def worker():
        try:
            run_auto_test_and_store(target)
        finally:
            # Clean up lock after done
            auto_test_locks.pop(target, None)
    threading.Thread(target=worker, daemon=True).start()
    return {"queued": True}

@app.get("/auto-test/results")
async def get_auto_test_results(target: str):
    """
    Fetch the most recent auto-test report for a given target.
    """
    report = auto_test_reports.get(target)
    if not report:
        raise HTTPException(status_code=404, detail="No report available for this target")
    return {"report": report}