"""
AI Gateway
Central gateway để quản lý và switch giữa các AI providers
"""

from typing import Dict, Any, Optional, List
from .base_provider import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .groq_provider import GroqProvider
from .vertex_provider import VertexAIProvider
from .config import AIConfig


class AIGateway:
    """
    Central gateway cho AI providers
    Cho phép switch giữa OpenAI, Anthropic, Google, v.v. một cách dễ dàng
    """
    
    # Map provider names đến provider classes
    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "groq": GroqProvider,
        "vertex": VertexAIProvider,
    }
    
    def __init__(self, config: Optional[AIConfig] = None):
        """
        Initialize gateway với configuration
        
        Args:
            config: AIConfig object (nếu None, sẽ tạo từ env variables)
        """
        self.config = config or AIConfig()
        self.config.validate()
        
        self._current_provider: Optional[BaseAIProvider] = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize provider dựa trên config"""
        provider_name = self.config.provider
        provider_class = self.PROVIDERS.get(provider_name)
        
        if not provider_class:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {list(self.PROVIDERS.keys())}"
            )
        
        provider_config = self.config.get_provider_config()
        self._current_provider = provider_class(**provider_config)
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với provider hiện tại
        
        Args:
            messages: List of message dicts
            tools: Optional tool definitions
            tool_choice: "auto", "required", hoặc "none"
            **kwargs: Additional parameters
            
        Returns:
            Normalized response dict
        """
        if not self._current_provider:
            raise RuntimeError("Provider not initialized")
        
        # Merge config defaults với kwargs
        params = {
            "temperature": self.config.temperature,
            **kwargs
        }
        
        return self._current_provider.chat_completion(
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            **params
        )
    
    def switch_provider(self, provider: str, model: Optional[str] = None):
        """
        Switch sang provider khác
        
        Args:
            provider: Provider name ("openai", "anthropic", "google")
            model: Optional model name
        """
        self.config.switch_provider(provider, model)
        self._initialize_provider()
    
    def get_current_provider(self) -> str:
        """Return tên của provider hiện tại"""
        return self.config.provider
    
    def get_current_model(self) -> str:
        """Return tên của model hiện tại"""
        return self.config.model
    
    def get_available_providers(self) -> Dict[str, bool]:
        """
        Lấy danh sách providers available (có API key)
        
        Returns:
            Dict mapping provider name -> bool
        """
        return self.config.get_available_providers()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về provider và model hiện tại
        
        Returns:
            Dict chứa provider name, model name, và các config
        """
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "available_providers": self.get_available_providers(),
            "available_models": self.config.get_available_models()
        }
    
    def set_model(self, model: str):
        """
        Chỉ thay đổi model mà không đổi provider
        
        Args:
            model: Model name
        """
        self.config.set_model(model)
        # Recreate provider với model mới
        self._initialize_provider()
    
    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Lấy danh sách models available
        
        Args:
            provider: Provider name (nếu None, dùng current provider)
            
        Returns:
            List of available models
        """
        return self.config.get_available_models(provider)
    
    @classmethod
    def create_from_dict(cls, config_dict: Dict[str, Any]) -> 'AIGateway':
        """
        Factory method để tạo gateway từ config dict
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            AIGateway instance
        """
        config = AIConfig(config_dict)
        return cls(config)
    
    @classmethod
    def create_from_env(cls) -> 'AIGateway':
        """
        Factory method để tạo gateway từ environment variables
        
        Returns:
            AIGateway instance
        """
        return cls(AIConfig())
