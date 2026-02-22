"""
AI Configuration Management
Quản lý config cho AI Gateway từ environment variables hoặc config dict
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()


class AIConfig:
    """
    Quản lý configuration cho AI Gateway
    Hỗ trợ nhiều providers và cho phép switch giữa chúng
    """
    
    # Default models cho từng provider
    DEFAULT_MODELS = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "google": "gemini-1.5-pro",
        "groq": "llama-3.3-70b-versatile",
        "vertex": "gemini-1.5-pro",
    }
    
    # Available models cho từng provider
    AVAILABLE_MODELS = {
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "google": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
        ],
        "groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "vertex": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
        ],
    }
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize config từ dict hoặc environment variables
        
        Args:
            config_dict: Optional dict chứa configuration
                Format: {
                    "provider": "openai",  # hoặc "anthropic", "google"
                    "model": "gpt-4o",
                    "api_keys": {
                        "openai": "sk-...",
                        "anthropic": "sk-ant-...",
                        "google": "..."
                    }
                }
        """
        self.config = config_dict or {}
        
        # Load từ environment nếu không có trong config_dict
        self.provider = self.config.get(
            "provider",
            os.getenv("AI_PROVIDER", "openai")
        ).lower()
        
        # Load API keys
        self.api_keys = self.config.get("api_keys", {})
        if not self.api_keys:
            self.api_keys = {
                "openai": os.getenv("OPENAI_API_KEY"),
                "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY"),
                "groq": os.getenv("GROQ_API_KEY"),
                "vertex": os.getenv("VERTEX_PROJECT_ID"),  # Vertex: project ID + service account file
            }
        
        # Store additional Vertex AI config
        self.vertex_location = self.config.get(
            "vertex_location",
            os.getenv("VERTEX_LOCATION", "us-central1")
        )
        self.vertex_credentials = self.config.get(
            "vertex_credentials",
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )
        
        # Load model name
        self.model = self.config.get(
            "model",
            os.getenv("AI_MODEL", self.DEFAULT_MODELS.get(self.provider))
        )
        
        # Additional config parameters
        self.temperature = float(self.config.get(
            "temperature",
            os.getenv("AI_TEMPERATURE", "0.7")
        ))
        
        self.max_tokens = int(self.config.get(
            "max_tokens",
            os.getenv("AI_MAX_TOKENS", "4096")
        ))
    
    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Lấy config cho một provider cụ thể
        
        Args:
            provider: Provider name (nếu None, dùng current provider)
            
        Returns:
            Dict chứa config cho provider
        """
        target_provider = provider or self.provider
        
        api_key = self.api_keys.get(target_provider)
        if not api_key:
            error_msg = f"API key not found for provider '{target_provider}'. "
            if target_provider == "vertex":
                error_msg += (
                    "Set VERTEX_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS environment variables. "
                    "GOOGLE_APPLICATION_CREDENTIALS should point to your service account JSON file."
                )
            else:
                error_msg += f"Set {target_provider.upper()}_API_KEY environment variable."
            raise ValueError(error_msg)
        
        config = {
            "api_key": api_key,
            "model": self.model if provider is None else self.DEFAULT_MODELS.get(target_provider),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        # Add Vertex-specific config
        if target_provider == "vertex":
            config["location"] = self.vertex_location
            if self.vertex_credentials:
                config["credentials_path"] = self.vertex_credentials
        
        return config
    
    def switch_provider(self, provider: str, model: Optional[str] = None):
        """
        Switch sang provider khác
        
        Args:
            provider: Provider name ("openai", "anthropic", "google")
            model: Optional model name (nếu None, dùng default model)
        """
        provider = provider.lower()
        if provider not in self.DEFAULT_MODELS:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported providers: {list(self.DEFAULT_MODELS.keys())}"
            )
        
        self.provider = provider
        if model:
            self.model = model
        else:
            self.model = self.DEFAULT_MODELS[provider]
    
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Check providers nào có API key available
        
        Returns:
            Dict mapping provider name -> bool (có API key hay không)
        """
        return {
            provider: bool(self.api_keys.get(provider))
            for provider in self.DEFAULT_MODELS.keys()
        }
    
    def validate(self) -> bool:
        """
        Validate config hiện tại
        
        Returns:
            True nếu config hợp lệ
            
        Raises:
            ValueError nếu config không hợp lệ
        """
        if self.provider not in self.DEFAULT_MODELS:
            raise ValueError(f"Invalid provider: {self.provider}")
        
        if not self.api_keys.get(self.provider):
            raise ValueError(f"No API key found for provider: {self.provider}")
        
        if not self.model:
            raise ValueError("Model name is required")
        
        return True
    
    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Lấy danh sách models available cho provider
        
        Args:
            provider: Provider name (nếu None, dùng current provider)
            
        Returns:
            List of model names
        """
        target_provider = provider or self.provider
        return self.AVAILABLE_MODELS.get(target_provider, [])
    
    def set_model(self, model: str):
        """
        Chỉ đổi model mà không đổi provider
        
        Args:
            model: Model name
        """
        # Validate model có trong danh sách không
        available = self.get_available_models()
        if available and model not in available:
            raise ValueError(
                f"Model '{model}' not available for provider '{self.provider}'. "
                f"Available models: {available}"
            )
        self.model = model
