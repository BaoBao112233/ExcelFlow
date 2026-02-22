"""
Groq Provider
Implementation cho Groq models (Llama, Mixtral, Gemma, etc.)
Groq sử dụng OpenAI-compatible API
"""

from typing import List, Dict, Any, Optional
import json

from .base_provider import BaseAIProvider

try:
    from openai import OpenAI
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqProvider(BaseAIProvider):
    """
    Provider cho Groq API
    Groq cung cấp inference cực nhanh cho các open-source models
    API tương thích với OpenAI
    """
    
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", **kwargs):
        if not GROQ_AVAILABLE:
            raise ImportError(
                "OpenAI package required for Groq provider. "
                "Install it with: pip install openai"
            )
        
        super().__init__(api_key, model, **kwargs)
        
        # Tạo OpenAI client với Groq base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.GROQ_BASE_URL
        )
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với Groq API
        """
        params = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        
        response = self.client.chat.completions.create(**params)
        return self.normalize_response(response)
    
    def normalize_response(self, raw_response: Any) -> Dict[str, Any]:
        """Convert Groq response sang format chuẩn (giống OpenAI)"""
        msg = raw_response.choices[0].message
        
        result = {
            "content": msg.content,
            "tool_calls": [],
            "finish_reason": raw_response.choices[0].finish_reason,
            "raw_message": msg
        }
        
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]
        
        return result
    
    def get_provider_name(self) -> str:
        return "groq"
