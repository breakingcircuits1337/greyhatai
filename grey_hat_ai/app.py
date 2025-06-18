"""
Main Streamlit Application for Grey Hat AI

This is the primary GUI interface for Grey Hat AI, providing:
- Unified command and control interface
- Multi-LLM support with dynamic switching
- Voice interaction capabilities
- Agent transparency and observability
- Autonomous testing workflows
"""

import streamlit as st
import threading
import queue
import time
import json
import logging
import traceback
from typing import Dict, Any, List, Optional
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import Grey Hat AI modules
from grey_hat_ai.llm_manager import LLMManager, LLMResponse
from grey_hat_ai.voice_engine import VoiceEngine, VoiceConfig
from grey_hat_ai.autonomous_web_agent import create_web_agent_tool

# Import CAI framework components
try:
    from cai.sdk.agents import Agent
    from cai.sdk.agents.tools import FunctionTool
    from cai.tools.reconnaissance.generic_linux_command import LinuxCmd
    from cai.tools.web.search_web import SearchWeb
    from cai.tools.misc.code_interpreter import Code
except ImportError as e:
    st.error(f"Failed to import CAI framework: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Grey Hat AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-indicator {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .agent-scratchpad {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
    .voice-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .voice-listening {
        background-color: #28a745;
        animation: pulse 1.5s infinite;
    }
    .voice-idle {
        background-color: #6c757d;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)


class GreyHatAI:
    """Main application class for Grey Hat AI."""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.voice_engine = None
        self.voice_queue = queue.Queue()
        self.agent = None
        self.web_tools = None
        
        # Initialize session state
        self._initialize_session_state()
        
        # Initialize components
        self._initialize_voice_engine()
        self._initialize_web_tools()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        
        if "agent_scratchpad" not in st.session_state:
            st.session_state.agent_scratchpad = []
        
        if "voice_listening" not in st.session_state:
            st.session_state.voice_listening = False
        
        if "api_keys_configured" not in st.session_state:
            st.session_state.api_keys_configured = {
                "gemini": False,
                "mistral": False,
                "groq": False,
                "elevenlabs": False
            }
        
        if "active_llm" not in st.session_state:
            st.session_state.active_llm = None
        
        if "target" not in st.session_state:
            st.session_state.target = ""
        
        if "auto_test_running" not in st.session_state:
            st.session_state.auto_test_running = False
    
    def _initialize_voice_engine(self):
        """Initialize the voice engine."""
        try:
            config = VoiceConfig()
            self.voice_engine = VoiceEngine(config)
            
            # Set up voice callbacks
            self.voice_engine.on_speech_detected = self._on_speech_detected
            self.voice_engine.on_listening_start = lambda: setattr(st.session_state, "voice_listening", True)
            self.voice_engine.on_listening_stop = lambda: setattr(st.session_state, "voice_listening", False)
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine: {e}")
            self.voice_engine = None
    
    def _initialize_web_tools(self):
        """Initialize web automation tools."""
        try:
            self.web_tools = create_web_agent_tool()
        except Exception as e:
            logger.error(f"Failed to initialize web tools: {e}")
            self.web_tools = None
    
    def _on_speech_detected(self, text: str):
        """Callback for when speech is detected."""
        self.voice_queue.put({"type": "speech", "text": text})
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        st.sidebar.markdown("## ⚙️ Configuration")
        
        # API Keys Section
        st.sidebar.markdown("### 🔑 API Keys")
        
        # Google Gemini
        gemini_key = st.sidebar.text_input(
            "Google Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key"
        )
        if gemini_key and gemini_key != st.session_state.get("gemini_key", ""):
            if self.llm_manager.set_api_key("gemini", gemini_key):
                st.session_state.api_keys_configured["gemini"] = True
                st.session_state.gemini_key = gemini_key
                st.sidebar.success("✅ Gemini configured")
            else:
                st.sidebar.error("❌ Gemini configuration failed")
        
        # Mistral AI
        mistral_key = st.sidebar.text_input(
            "Mistral AI API Key",
            type="password",
            help="Enter your Mistral AI API key"
        )
        if mistral_key and mistral_key != st.session_state.get("mistral_key", ""):
            if self.llm_manager.set_api_key("mistral", mistral_key):
                st.session_state.api_keys_configured["mistral"] = True
                st.session_state.mistral_key = mistral_key
                st.sidebar.success("✅ Mistral configured")
            else:
                st.sidebar.error("❌ Mistral configuration failed")
        
        # Groq
        groq_key = st.sidebar.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key"
        )
        if groq_key and groq_key != st.session_state.get("groq_key", ""):
            if self.llm_manager.set_api_key("groq", groq_key):
                st.session_state.api_keys_configured["groq"] = True
                st.session_state.groq_key = groq_key
                st.sidebar.success("✅ Groq configured")
            else:
                st.sidebar.error("❌ Groq configuration failed")
        
        # Eleven Labs
        elevenlabs_key = st.sidebar.text_input(
            "Eleven Labs API Key",
            type="password",
            help="Enter your Eleven Labs API key for TTS"
        )
        if elevenlabs_key and elevenlabs_key != st.session_state.get("elevenlabs_key", ""):
            if self.voice_engine and self.voice_engine.set_elevenlabs_api_key(elevenlabs_key):
                st.session_state.api_keys_configured["elevenlabs"] = True
                st.session_state.elevenlabs_key = elevenlabs_key
                st.sidebar.success("✅ Eleven Labs configured")
            else:
                st.sidebar.error("❌ Eleven Labs configuration failed")
        
        st.sidebar.markdown("---")
        
        # LLM Selection
        st.sidebar.markdown("### 🤖 LLM Selection")
        
        # Get available providers
        configured_providers = [p for p, configured in st.session_state.api_keys_configured.items() 
                              if configured and p != "elevenlabs"]
        
        if configured_providers:
            selected_provider = st.sidebar.selectbox(
                "Active LLM Provider",
                configured_providers,
                help="Select the active LLM provider"
            )
            
            # Get available models for selected provider
            available_models = self.llm_manager.get_available_models(selected_provider)
            if selected_provider in available_models:
                selected_model = st.sidebar.selectbox(
                    "Model",
                    available_models[selected_provider],
                    help=f"Select the {selected_provider} model to use"
                )
                
                # Set active model
                if st.sidebar.button("🔄 Set Active Model"):
                    if self.llm_manager.set_active_model(selected_provider, selected_model):
                        st.session_state.active_llm = f"{selected_provider}:{selected_model}"
                        st.sidebar.success(f"✅ Active: {selected_provider}:{selected_model}")
                    else:
                        st.sidebar.error("❌ Failed to set active model")
        else:
            st.sidebar.warning("⚠️ Configure at least one LLM API key")
        
        st.sidebar.markdown("---")
        
        # Voice Configuration
        st.sidebar.markdown("### 🎤 Voice Settings")
        
        if self.voice_engine:
            # Voice status indicator
            voice_status = "🟢 Listening" if st.session_state.voice_listening else "🔴 Idle"
            st.sidebar.markdown(f"**Status:** {voice_status}")
            
            # Voice controls
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("🎤 Start Voice"):
                    if not st.session_state.voice_listening:
                        self.voice_engine.start_listening()
                        st.rerun()
            
            with col2:
                if st.button("🔇 Stop Voice"):
                    if st.session_state.voice_listening:
                        self.voice_engine.stop_listening()
                        st.rerun()
            
            # Voice model selection (if Eleven Labs configured)
            if st.session_state.api_keys_configured.get("elevenlabs", False):
                voices = self.voice_engine.get_available_voices()
                if voices:
                    selected_voice = st.sidebar.selectbox(
                        "TTS Voice",
                        list(voices.keys()),
                        format_func=lambda x: voices[x],
                        help="Select text-to-speech voice"
                    )
                    self.voice_engine.config.elevenlabs_voice_id = selected_voice
        else:
            st.sidebar.warning("⚠️ Voice engine not available")
        
        st.sidebar.markdown("---")
        
        # Target Configuration
        st.sidebar.markdown("### 🎯 Target Settings")
        
        target = st.sidebar.text_input(
            "Target",
            value=st.session_state.target,
            placeholder="IP address, URL, or domain",
            help="Enter the target for reconnaissance and testing"
        )
        st.session_state.target = target
        
        # Auto Test Controls
        if st.sidebar.button("🚀 Start Auto Test", disabled=not target or st.session_state.auto_test_running):
            st.session_state.auto_test_running = True
            self._start_auto_test(target)
        
        if st.sidebar.button("⏹️ Stop Auto Test", disabled=not st.session_state.auto_test_running):
            st.session_state.auto_test_running = False
        
        st.sidebar.markdown("---")
        
        # System Status
        st.sidebar.markdown("### 📊 System Status")
        
        # LLM Manager Status
        llm_status = self.llm_manager.get_status()
        st.sidebar.markdown(f"**Active LLM:** {llm_status.get('active_provider', 'None')}:{llm_status.get('active_model', 'None')}")
        
        # Voice Engine Status
        if self.voice_engine:
            voice_status = self.voice_engine.get_status()
            st.sidebar.markdown(f"**Voice STT:** {'✅' if voice_status['whisper_available'] else '❌'}")
            st.sidebar.markdown(f"**Voice TTS:** {'✅' if voice_status['elevenlabs_configured'] else '❌'}")
        
        # Web Agent Status
        st.sidebar.markdown(f"**Web Agent:** {'✅' if self.web_tools else '❌'}")
    
    def render_main_interface(self):
        """Render the main interface."""
        # Header
        st.markdown('<div class="main-header">🎯 Grey Hat AI</div>', unsafe_allow_html=True)
        st.markdown("*Advanced Cybersecurity AI Framework with GUI and Voice Integration*")
        
        # Main layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self.render_conversation_panel()
        
        with col2:
            self.render_agent_scratchpad()
    
    def render_conversation_panel(self):
        """Render the conversation panel."""
        st.markdown("### 💬 Conversation")
        
        # Display conversation history
        conversation_container = st.container()
        
        with conversation_container:
            for message in st.session_state.conversation_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # User input
        user_input = st.chat_input("Enter your message or use voice input...")
        
        # Process voice input
        self._process_voice_input()
        
        # Process user input
        if user_input:
            self._process_user_input(user_input)
    
    def render_agent_scratchpad(self):
        """Render the agent scratchpad for transparency."""
        st.markdown("### 🧠 Agent Scratchpad")
        st.markdown("*Real-time view of agent's reasoning and actions*")
        
        # Create scrollable container for scratchpad
        scratchpad_container = st.container()
        
        with scratchpad_container:
            if st.session_state.agent_scratchpad:
                scratchpad_text = "\\n".join(st.session_state.agent_scratchpad)
                st.markdown(f'<div class="agent-scratchpad">{scratchpad_text}</div>', 
                          unsafe_allow_html=True)
            else:
                st.info("Agent scratchpad will appear here during operation...")
    
    def _process_voice_input(self):
        """Process voice input from the queue."""
        try:
            while not self.voice_queue.empty():
                voice_data = self.voice_queue.get_nowait()
                if voice_data["type"] == "speech":
                    text = voice_data["text"]
                    st.info(f"🎤 Voice input: {text}")
                    self._process_user_input(text)
        except queue.Empty:
            pass
    
    def _process_user_input(self, user_input: str):
        """Process user input and generate agent response."""
        # Add user message to conversation
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Add to scratchpad
        st.session_state.agent_scratchpad.append(f"USER: {user_input}")
        
        # Generate response
        if st.session_state.active_llm:
            try:
                # Prepare conversation history for LLM
                history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.conversation_history[:-1]  # Exclude current message
                ]
                
                # Add reasoning to scratchpad
                st.session_state.agent_scratchpad.append("REASONING: Analyzing user request and determining appropriate response...")
                
                # Generate response
                response = self.llm_manager.generate_response(user_input, history)
                
                if response:
                    # Add assistant response to conversation
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Add to scratchpad
                    st.session_state.agent_scratchpad.append(f"ACTION: Generated response using {response.provider}:{response.model}")
                    st.session_state.agent_scratchpad.append(f"RESPONSE: {response.content[:100]}...")
                    
                    # Generate TTS if configured
                    if (self.voice_engine and 
                        st.session_state.api_keys_configured.get("elevenlabs", False)):
                        try:
                            audio_data = self.voice_engine.text_to_speech(response.content)
                            if audio_data:
                                self.voice_engine.play_audio(audio_data)
                        except Exception as e:
                            logger.error(f"TTS error: {e}")
                else:
                    st.error("Failed to generate response")
                    st.session_state.agent_scratchpad.append("ERROR: Failed to generate response")
                    
            except Exception as e:
                st.error(f"Error processing input: {e}")
                st.session_state.agent_scratchpad.append(f"ERROR: {str(e)}")
        else:
            st.warning("Please configure and select an LLM first")
        
        # Rerun to update the interface
        st.rerun()
    
    def _start_auto_test(self, target: str):
        """Start autonomous testing workflow."""
        st.session_state.agent_scratchpad.append(f"AUTO TEST: Starting autonomous test for target: {target}")
        
        # This would implement the full auto test workflow
        # For now, just add a placeholder
        auto_test_prompt = f"""
        I need you to perform a comprehensive security assessment of the target: {target}
        
        Please follow these phases:
        1. Reconnaissance - Gather information about the target
        2. Vulnerability Analysis - Identify potential security issues
        3. Exploitation Planning - Suggest potential attack vectors (DO NOT execute without permission)
        4. Reporting - Summarize findings
        
        Use available tools as needed and maintain transparency in your reasoning.
        """
        
        self._process_user_input(auto_test_prompt)
    
    def run(self):
        """Run the main application."""
        try:
            # Render sidebar
            self.render_sidebar()
            
            # Render main interface
            self.render_main_interface()
            
            # Auto-refresh for voice input
            if st.session_state.voice_listening:
                time.sleep(0.1)
                st.rerun()
                
        except Exception as e:
            st.error(f"Application error: {e}")
            st.error(traceback.format_exc())


def main():
    """Main entry point for the application."""
    try:
        app = GreyHatAI()
        app.run()
    except Exception as e:
        st.error(f"Failed to start Grey Hat AI: {e}")
        st.error(traceback.format_exc())


if __name__ == "__main__":
    main()

