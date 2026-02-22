"""
Base Provider Interface
Abstract class định nghĩa interface cho tất cả AI providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseAIProvider(ABC):
    """
    Abstract base class cho tất cả AI providers
    Mọi provider phải implement các method này
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize provider với API key và model name
        
        Args:
            api_key: API key cho provider
            model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với tool calling support
        
        Args:
            messages: List of message dicts với 'role' và 'content'
            tools: Optional list of tool definitions
            tool_choice: "auto", "required", hoặc "none"
            **kwargs: Additional parameters
            
        Returns:
            Dict chứa response với format chuẩn:
            {
                "content": str,  # Text response từ AI
                "tool_calls": List[Dict],  # Danh sách tool calls (nếu có)
                "finish_reason": str  # "stop", "tool_calls", etc.
            }
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return tên của provider (e.g., "openai", "anthropic")"""
        pass
    
    def normalize_tool_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert tools từ OpenAI format sang format của provider
        Default implementation giữ nguyên OpenAI format
        Override method này nếu provider cần format khác
        """
        return tools
    
    def normalize_response(self, raw_response: Any) -> Dict[str, Any]:
        """
        Convert response từ provider-specific format sang format chuẩn
        Override method này để handle response format của từng provider
        """
        return {
            "content": None,
            "tool_calls": [],
            "finish_reason": "stop"
        }
