"""
Anthropic Provider
Implementation cho Anthropic Claude models
"""

from typing import List, Dict, Any, Optional
import json

from .base_provider import BaseAIProvider

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(BaseAIProvider):
    """Provider cho Anthropic Claude API"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. "
                "Install it with: pip install anthropic"
            )
        
        super().__init__(api_key, model, **kwargs)
        self.client = Anthropic(api_key=self.api_key)
        self.max_tokens = kwargs.get("max_tokens", 4096)
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với Anthropic Claude API
        """
        # Anthropic yêu cầu system message riêng
        system_message = None
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        params = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": claude_messages,
        }
        
        if system_message:
            params["system"] = system_message
        
        if tools:
            # Convert OpenAI tool format sang Anthropic format
            params["tools"] = self.normalize_tool_format(tools)
            if tool_choice == "required":
                params["tool_choice"] = {"type": "any"}
            elif tool_choice != "none":
                params["tool_choice"] = {"type": "auto"}
        
        response = self.client.messages.create(**params)
        return self.normalize_response(response)
    
    def normalize_tool_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI tool format sang Anthropic tool format
        OpenAI: {"type": "function", "function": {...}}
        Anthropic: {"name": ..., "description": ..., "input_schema": {...}}
        """
        anthropic_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {})
                })
        return anthropic_tools
    
    def normalize_response(self, raw_response: Any) -> Dict[str, Any]:
        """Convert Anthropic response sang format chuẩn"""
        result = {
            "content": None,
            "tool_calls": [],
            "finish_reason": raw_response.stop_reason,
            "raw_message": raw_response
        }
        
        # Anthropic có thể trả về nhiều content blocks
        for block in raw_response.content:
            if block.type == "text":
                result["content"] = block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input)
                    }
                })
        
        return result
    
    def get_provider_name(self) -> str:
        return "anthropic"
