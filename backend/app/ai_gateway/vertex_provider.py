"""
Vertex AI Provider
Implementation cho Google Vertex AI (Enterprise-grade Gemini)
"""

from typing import List, Dict, Any, Optional
import json

from .base_provider import BaseAIProvider

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, Content
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False


class VertexAIProvider(BaseAIProvider):
    """
    Provider cho Google Vertex AI
    Enterprise version của Gemini với better SLA và security
    
    Authentication: Sử dụng service account JSON file
    Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    """
    
    def __init__(
        self, 
        api_key: str,  # Vertex dùng project_id (không phải API key thông thường)
        model: str = "gemini-1.5-pro",
        **kwargs
    ):
        if not VERTEX_AVAILABLE:
            raise ImportError(
                "Vertex AI package not installed. "
                "Install it with: pip install google-cloud-aiplatform"
            )
        
        super().__init__(api_key, model, **kwargs)
        
        # For Vertex, api_key is actually project_id
        self.project_id = api_key
        self.location = kwargs.get("location", "us-central1")
        
        # Verify service account credentials
        import os
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError(
                "Vertex AI requires GOOGLE_APPLICATION_CREDENTIALS environment variable. "
                "Set it to the path of your service account JSON file. "
                "Example: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"
            )
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Service account file not found: {credentials_path}. "
                "Make sure GOOGLE_APPLICATION_CREDENTIALS points to a valid JSON file."
            )
        
        # Initialize Vertex AI with credentials
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.client = GenerativeModel(self.model)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Vertex AI: {str(e)}. "
                "Check that your service account has 'Vertex AI User' role and API is enabled."
            )
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tạo chat completion với Vertex AI
        """
        # Convert messages sang Vertex format
        vertex_contents = self._convert_messages(messages)
        
        generation_config = kwargs.get("generation_config", {
            "temperature": kwargs.get("temperature", 0.7),
            "max_output_tokens": kwargs.get("max_tokens", 8192),
        })
        
        # Convert tools nếu có
        vertex_tools = None
        if tools:
            vertex_tools = self.normalize_tool_format(tools)
        
        # Generate content
        response = self.client.generate_content(
            contents=vertex_contents,
            tools=vertex_tools,
            generation_config=generation_config
        )
        
        return self.normalize_response(response)
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Content]:
        """
        Convert OpenAI message format sang Vertex AI Content format
        """
        vertex_contents = []
        
        for msg in messages:
            role = msg["role"]
            
            # Vertex AI dùng "user" và "model"
            if role == "assistant":
                role = "model"
            elif role == "system":
                # System messages có thể prepend vào user message đầu tiên
                continue
            
            content = Content(
                role=role,
                parts=[Part.from_text(msg["content"])]
            )
            vertex_contents.append(content)
        
        return vertex_contents
    
    def normalize_tool_format(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """
        Convert OpenAI tool format sang Vertex AI tool format
        """
        from vertexai.generative_models import Tool, FunctionDeclaration
        
        function_declarations = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                
                function_declarations.append(
                    FunctionDeclaration(
                        name=func["name"],
                        description=func.get("description", ""),
                        parameters=func.get("parameters", {})
                    )
                )
        
        return [Tool(function_declarations=function_declarations)] if function_declarations else None
    
    def normalize_response(self, raw_response: Any) -> Dict[str, Any]:
        """Convert Vertex AI response sang format chuẩn"""
        result = {
            "content": None,
            "tool_calls": [],
            "finish_reason": "stop",
            "raw_message": raw_response
        }
        
        # Get text content
        if hasattr(raw_response, 'text'):
            result["content"] = raw_response.text
        
        # Check for function calls
        if hasattr(raw_response, 'candidates') and raw_response.candidates:
            candidate = raw_response.candidates[0]
            
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        fc = part.function_call
                        
                        # Convert function call args to dict
                        args_dict = {}
                        if hasattr(fc, 'args'):
                            for key, value in fc.args.items():
                                args_dict[key] = value
                        
                        result["tool_calls"].append({
                            "id": f"call_{fc.name}",
                            "type": "function",
                            "function": {
                                "name": fc.name,
                                "arguments": json.dumps(args_dict)
                            }
                        })
        
        return result
    
    def get_provider_name(self) -> str:
        return "vertex"
