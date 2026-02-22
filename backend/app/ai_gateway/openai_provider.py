"""
OpenAI Provider
Implementation cho OpenAI models (GPT-4, GPT-4o, etc.)
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

from .base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """Provider cho OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = OpenAI(api_key=self.api_key)
        
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với OpenAI API
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
        """Convert OpenAI response sang format chuẩn"""
        msg = raw_response.choices[0].message
        
        result = {
            "content": msg.content,
            "tool_calls": [],
            "finish_reason": raw_response.choices[0].finish_reason,
            "raw_message": msg  # Giữ lại message object gốc để dùng tiếp
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
        return "openai"
