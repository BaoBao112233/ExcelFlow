"""
Google Provider
Implementation cho Google Gemini models
"""

from typing import List, Dict, Any, Optional
import json

from .base_provider import BaseAIProvider

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleProvider(BaseAIProvider):
    """Provider cho Google Gemini API"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", **kwargs):
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google Generative AI package not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với Google Gemini API
        """
        # Convert messages sang Gemini format
        gemini_messages = self._convert_messages(messages)
        
        generation_config = kwargs.get("generation_config", {})
        
        params = {
            "contents": gemini_messages,
            "generation_config": generation_config
        }
        
        if tools:
            # Convert tools sang Gemini format
            params["tools"] = self.normalize_tool_format(tools)
        
        response = self.client.generate_content(**params)
        return self.normalize_response(response)
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI message format sang Gemini format
        Gemini dùng "user" và "model" thay vì "user" và "assistant"
        """
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "assistant":
                role = "model"
            elif role == "system":
                # Gemini không có system role riêng, gộp vào user message đầu tiên
                continue
            
            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        return gemini_messages
    
    def normalize_tool_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI tool format sang Google Gemini format
        """
        gemini_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                gemini_tools.append({
                    "function_declarations": [{
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {})
                    }]
                })
        return gemini_tools
    
    def normalize_response(self, raw_response: Any) -> Dict[str, Any]:
        """Convert Google Gemini response sang format chuẩn"""
        result = {
            "content": None,
            "tool_calls": [],
            "finish_reason": "stop",
            "raw_message": raw_response
        }
        
        if raw_response.text:
            result["content"] = raw_response.text
        
        # Check for function calls
        if hasattr(raw_response, 'candidates') and raw_response.candidates:
            candidate = raw_response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        fc = part.function_call
                        result["tool_calls"].append({
                            "id": f"call_{fc.name}",  # Gemini không có ID riêng
                            "type": "function",
                            "function": {
                                "name": fc.name,
                                "arguments": json.dumps(dict(fc.args))
                            }
                        })
        
        return result
    
    def get_provider_name(self) -> str:
        return "google"
