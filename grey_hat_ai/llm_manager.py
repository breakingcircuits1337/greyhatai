"""
LLM Manager for Grey Hat AI

This module provides a unified interface for interacting with multiple LLM providers:
- Google Gemini
- Mistral AI
- Groq

The LLMManager class abstracts the differences between these APIs and provides
a consistent interface for the main application.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralClient = None
    ChatMessage = None

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standardized response format for all LLM providers."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
    raw_response: Optional[Any] = None


class LLMManager:
    """
    Unified interface for multiple LLM providers.
    
    Supports Google Gemini, Mistral AI, and Groq APIs with automatic
    request formatting and response parsing.
    """
    
    SUPPORTED_PROVIDERS = {
        "gemini": {
            "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"],
            "default_model": "gemini-1.5-pro"
        },
        "mistral": {
            "models": ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest", "codestral-latest"],
            "default_model": "mistral-large-latest"
        },
        "groq": {
            "models": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
            "default_model": "llama3-70b-8192"
        }
    }
    
    def __init__(self):
        self.active_provider = None
        self.active_model = None
        self.clients = {}
        self._api_keys = {}
        
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        Set API key for a specific provider.
        
        Args:
            provider: The LLM provider name (gemini, mistral, groq)
            api_key: The API key for the provider
            
        Returns:
            bool: True if successful, False otherwise
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            logger.error(f"Unsupported provider: {provider}")
            return False
            
        self._api_keys[provider] = api_key
        
        try:
            if provider == "gemini" and genai:
                genai.configure(api_key=api_key)
                self.clients[provider] = genai
                
            elif provider == "mistral" and MistralClient:
                self.clients[provider] = MistralClient(api_key=api_key)
                
            elif provider == "groq" and Groq:
                self.clients[provider] = Groq(api_key=api_key)
                
            else:
                logger.error(f"Provider {provider} not available (missing dependencies)")
                return False
                
            logger.info(f"Successfully configured {provider} client")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure {provider} client: {e}")
            return False
    
    def set_active_model(self, provider: str, model: str = None) -> bool:
        """
        Set the active LLM provider and model.
        
        Args:
            provider: The LLM provider name
            model: The specific model name (optional, uses default if not provided)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            logger.error(f"Unsupported provider: {provider}")
            return False
            
        if provider not in self.clients:
            logger.error(f"Provider {provider} not configured. Set API key first.")
            return False
            
        if model is None:
            model = self.SUPPORTED_PROVIDERS[provider]["default_model"]
        elif model not in self.SUPPORTED_PROVIDERS[provider]["models"]:
            logger.warning(f"Model {model} not in known models for {provider}, proceeding anyway")
            
        self.active_provider = provider
        self.active_model = model
        logger.info(f"Active model set to {provider}:{model}")
        return True
    
    def generate_response(self, 
                         prompt: str, 
                         history: List[Dict[str, str]] = None,
                         max_tokens: int = 4000,
                         temperature: float = 0.7) -> Optional[LLMResponse]:
        """
        Generate a response using the active LLM.
        
        Args:
            prompt: The user's input prompt
            history: Conversation history in format [{"role": "user/assistant", "content": "..."}]
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            LLMResponse object or None if failed
        """
        if not self.active_provider or not self.active_model:
            logger.error("No active model set. Call set_active_model() first.")
            return None
            
        if history is None:
            history = []
            
        try:
            if self.active_provider == "gemini":
                return self._generate_gemini(prompt, history, max_tokens, temperature)
            elif self.active_provider == "mistral":
                return self._generate_mistral(prompt, history, max_tokens, temperature)
            elif self.active_provider == "groq":
                return self._generate_groq(prompt, history, max_tokens, temperature)
            else:
                logger.error(f"Unknown provider: {self.active_provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response with {self.active_provider}: {e}")
            return None
    
    def _generate_gemini(self, prompt: str, history: List[Dict[str, str]], 
                        max_tokens: int, temperature: float) -> LLMResponse:
        """Generate response using Google Gemini."""
        model = genai.GenerativeModel(self.active_model)
        
        # Convert history to Gemini format
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})
        
        # Start chat with history
        chat = model.start_chat(history=chat_history)
        
        # Generate response
        response = chat.send_message(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        return LLMResponse(
            content=response.text,
            model=self.active_model,
            provider="gemini",
            usage={"prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                   "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None},
            raw_response=response
        )
    
    def _generate_mistral(self, prompt: str, history: List[Dict[str, str]], 
                         max_tokens: int, temperature: float) -> LLMResponse:
        """Generate response using Mistral AI."""
        client = self.clients["mistral"]
        
        # Convert history to Mistral format
        messages = []
        for msg in history:
            messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
        
        # Add current prompt
        messages.append(ChatMessage(role="user", content=prompt))
        
        # Generate response
        response = client.chat(
            model=self.active_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.active_model,
            provider="mistral",
            usage={"prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                   "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None},
            raw_response=response
        )
    
    def _generate_groq(self, prompt: str, history: List[Dict[str, str]], 
                      max_tokens: int, temperature: float) -> LLMResponse:
        """Generate response using Groq."""
        client = self.clients["groq"]
        
        # Convert history to OpenAI format (Groq uses OpenAI-compatible API)
        messages = []
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Generate response
        response = client.chat.completions.create(
            model=self.active_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.active_model,
            provider="groq",
            usage={"prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                   "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None},
            raw_response=response
        )
    
    def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """
        Get available models for providers.
        
        Args:
            provider: Specific provider to get models for (optional)
            
        Returns:
            Dictionary mapping provider names to model lists
        """
        if provider:
            if provider in self.SUPPORTED_PROVIDERS:
                return {provider: self.SUPPORTED_PROVIDERS[provider]["models"]}
            else:
                return {}
        else:
            return {p: info["models"] for p, info in self.SUPPORTED_PROVIDERS.items()}
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available (dependencies installed and configured)."""
        if provider not in self.SUPPORTED_PROVIDERS:
            return False
            
        if provider == "gemini":
            return genai is not None and provider in self.clients
        elif provider == "mistral":
            return MistralClient is not None and provider in self.clients
        elif provider == "groq":
            return Groq is not None and provider in self.clients
            
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the LLM manager."""
        return {
            "active_provider": self.active_provider,
            "active_model": self.active_model,
            "configured_providers": list(self.clients.keys()),
            "available_providers": {
                "gemini": genai is not None,
                "mistral": MistralClient is not None,
                "groq": Groq is not None
            }
        }

