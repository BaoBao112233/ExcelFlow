"""
Example script demonstrating AI Gateway usage
Ví dụ cách sử dụng AI Gateway để switch giữa các providers
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai_gateway import AIGateway, AIConfig


def example_1_basic_usage():
    """Ví dụ 1: Sử dụng cơ bản với env variables"""
    print("=" * 60)
    print("VÍ DỤ 1: Sử dụng cơ bản")
    print("=" * 60)
    
    # Tạo gateway từ environment variables
    gateway = AIGateway.create_from_env()
    
    # Xem thông tin provider hiện tại
    info = gateway.get_provider_info()
    print(f"\nProvider hiện tại: {info['provider']}")
    print(f"Model: {info['model']}")
    print(f"Available providers: {info['available_providers']}")
    
    # Test chat completion
    messages = [
        {"role": "user", "content": "Hello! What is 2+2?"}
    ]
    
    print(f"\nGửi message: {messages[0]['content']}")
    response = gateway.chat_completion(messages)
    print(f"Response: {response['content']}")


def example_2_custom_config():
    """Ví dụ 2: Tạo gateway với custom config"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: Custom configuration")
    print("=" * 60)
    
    # Tạo custom config
    config = AIConfig({
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.3,  # Temperature thấp hơn cho output consistent hơn
        "max_tokens": 2000,
        "api_keys": {
            "openai": os.getenv("OPENAI_API_KEY")
        }
    })
    
    gateway = AIGateway(config)
    print(f"\nĐã tạo gateway với:")
    print(f"  Provider: {gateway.get_current_provider()}")
    print(f"  Model: {gateway.get_current_model()}")
    print(f"  Temperature: {gateway.config.temperature}")


def example_3_switch_providers():
    """Ví dụ 3: Switch giữa các providers"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: Switch giữa các providers")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    # Test message
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    # Get available providers
    available = gateway.get_available_providers()
    print(f"\nAvailable providers: {available}")
    
    # Test với từng provider có API key
    for provider_name, is_available in available.items():
        if not is_available:
            print(f"\n❌ {provider_name.upper()}: Không có API key, skip")
            continue
        
        print(f"\n✅ Testing {provider_name.upper()}...")
        
        try:
            # Switch sang provider này
            gateway.switch_provider(provider_name)
            print(f"   Model: {gateway.get_current_model()}")
            
            # Send request
            response = gateway.chat_completion(messages)
            print(f"   Response: {response['content'][:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def example_4_with_tools():
    """Ví dụ 4: Sử dụng với function calling/tools"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 4: Function calling với tools")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]
    
    messages = [
        {"role": "user", "content": "What's the weather in Paris?"}
    ]
    
    print(f"\nProvider: {gateway.get_current_provider()}")
    print(f"Message: {messages[0]['content']}")
    
    response = gateway.chat_completion(
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    if response['tool_calls']:
        print(f"\n✅ AI muốn gọi function:")
        for tool_call in response['tool_calls']:
            print(f"   Function: {tool_call['function']['name']}")
            print(f"   Arguments: {tool_call['function']['arguments']}")
    else:
        print(f"\n❌ Không có tool call")
        print(f"Response: {response['content']}")


def example_5_compare_providers():
    """Ví dụ 5: So sánh response từ các providers khác nhau"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 5: So sánh providers")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    # Creative task
    messages = [
        {"role": "user", "content": "Write a haiku about coding"}
    ]
    
    available = gateway.get_available_providers()
    
    print("\nPrompt: Write a haiku about coding\n")
    
    for provider_name, is_available in available.items():
        if not is_available:
            continue
        
        try:
            gateway.switch_provider(provider_name)
            response = gateway.chat_completion(messages, temperature=0.9)
            
            print(f"\n{provider_name.upper()} ({gateway.get_current_model()}):")
            print("-" * 40)
            print(response['content'])
            
        except Exception as e:
            print(f"\n{provider_name.upper()}: Error - {str(e)}")


if __name__ == "__main__":
    print("\n🚀 AI GATEWAY EXAMPLES\n")
    
    try:
        # Chạy các examples
        example_1_basic_usage()
        example_2_custom_config()
        example_3_switch_providers()
        example_4_with_tools()
        example_5_compare_providers()
        
        print("\n" + "=" * 60)
        print("✅ Hoàn thành tất cả examples!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
