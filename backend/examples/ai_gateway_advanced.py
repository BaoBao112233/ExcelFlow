"""
Advanced examples demonstrating Groq and Vertex AI providers
"""

import os
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai_gateway import AIGateway, AIConfig


def example_groq_speed_test():
    """Demo Groq's incredible speed"""
    print("=" * 60)
    print("GROQ SPEED TEST - Ultra fast inference!")
    print("=" * 60)
    
    try:
        gateway = AIGateway.create_from_env()
        
        # Switch to Groq
        gateway.switch_provider("groq", "llama-3.3-70b-versatile")
        
        import time
        
        messages = [
            {"role": "user", "content": "Explain quantum computing in 3 sentences."}
        ]
        
        print(f"\nUsing Groq - {gateway.get_current_model()}")
        print(f"Query: {messages[0]['content']}\n")
        
        start = time.time()
        response = gateway.chat_completion(messages)
        elapsed = time.time() - start
        
        print(f"Response ({elapsed:.2f}s):")
        print(response['content'])
        print(f"\n⚡ Groq inference time: {elapsed:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Groq not available: {str(e)}")
        print("Setup: https://console.groq.com/")


def example_compare_all_providers():
    """Compare response from ALL 5 providers"""
    print("\n" + "=" * 60)
    print("COMPARE ALL PROVIDERS")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    prompt = "Write a one-line description of AI in a creative way."
    messages = [{"role": "user", "content": prompt}]
    
    print(f"\nPrompt: {prompt}\n")
    
    # All 5 providers
    providers_to_test = ["openai", "anthropic", "google", "groq", "vertex"]
    
    for provider in providers_to_test:
        try:
            # Check if available
            available = gateway.get_available_providers()
            if not available.get(provider):
                print(f"❌ {provider.upper()}: API key not configured\n")
                continue
            
            # Switch and test
            gateway.switch_provider(provider)
            info = gateway.get_provider_info()
            
            print(f"✅ {provider.upper()} ({info['model']}):")
            print("-" * 60)
            
            import time
            start = time.time()
            response = gateway.chat_completion(messages, temperature=0.9)
            elapsed = time.time() - start
            
            print(f"{response['content']}")
            print(f"⏱️  Time: {elapsed:.2f}s\n")
            
        except Exception as e:
            print(f"❌ {provider.upper()}: {str(e)}\n")


def example_model_selection():
    """Demo selecting different models within a provider"""
    print("\n" + "=" * 60)
    print("MODEL SELECTION DEMO")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    # Test with Groq (có nhiều models)
    try:
        gateway.switch_provider("groq")
        
        # Get available models
        models = gateway.get_available_models()
        print(f"\nAvailable Groq models: {models}\n")
        
        # Test với các models khác nhau
        test_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        
        for model in test_models:
            if model not in models:
                continue
                
            print(f"\nTesting {model}:")
            print("-" * 40)
            
            gateway.set_model(model)
            
            messages = [{"role": "user", "content": "Count from 1 to 5."}]
            
            import time
            start = time.time()
            response = gateway.chat_completion(messages)
            elapsed = time.time() - start
            
            print(f"Response: {response['content']}")
            print(f"Time: {elapsed:.2f}s")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def example_vertex_enterprise():
    """Demo Vertex AI for enterprise use"""
    print("\n" + "=" * 60)
    print("VERTEX AI ENTERPRISE DEMO")
    print("=" * 60)
    
    try:
        gateway = AIGateway.create_from_env()
        
        # Check if Vertex is configured
        available = gateway.get_available_providers()
        if not available.get("vertex"):
            print("\n❌ Vertex AI not configured")
            print("Setup guide: docs/VERTEX_SETUP.md")
            print("\nQuick setup:")
            print("1. Create GCP project")
            print("2. Enable Vertex AI API")
            print("3. Set VERTEX_PROJECT_ID in .env")
            return
        
        # Switch to Vertex
        gateway.switch_provider("vertex", "gemini-1.5-pro")
        
        print(f"\n✅ Using Vertex AI - Enterprise Gemini")
        print(f"Provider: {gateway.get_current_provider()}")
        print(f"Model: {gateway.get_current_model()}")
        
        # Test with long context (Vertex excels at this)
        messages = [
            {
                "role": "user", 
                "content": """Analyze this data structure and suggest improvements:
                
                data = {
                    'users': [
                        {'id': 1, 'name': 'Alice', 'age': 30},
                        {'id': 2, 'name': 'Bob', 'age': 25}
                    ],
                    'settings': {'theme': 'dark', 'lang': 'en'}
                }
                """
            }
        ]
        
        response = gateway.chat_completion(messages)
        print(f"\nResponse:\n{response['content']}")
        
        print("\n🏢 Vertex AI features:")
        print("- Enterprise SLA")
        print("- Data privacy guarantees")
        print("- VPC support")
        print("- 2M token context window")
        
    except Exception as e:
        print(f"❌ Vertex AI error: {str(e)}")


def example_smart_routing():
    """Demo automatically choosing best provider for task"""
    print("\n" + "=" * 60)
    print("SMART ROUTING - Auto-select best provider")
    print("=" * 60)
    
    gateway = AIGateway.create_from_env()
    
    tasks = [
        {
            "type": "speed",
            "query": "What's 15 * 23?",
            "provider": "groq",
            "model": "llama-3.1-8b-instant"
        },
        {
            "type": "reasoning",
            "query": "Explain the philosophical implications of AI consciousness.",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        },
        {
            "type": "cost-effective",
            "query": "What's the capital of France?",
            "provider": "groq",
            "model": "llama-3.3-70b-versatile"
        },
        {
            "type": "long-context",
            "query": "Summarize this: " + "data " * 100,  # Long context
            "provider": "vertex",
            "model": "gemini-1.5-pro"
        }
    ]
    
    for task in tasks:
        print(f"\n{'='*60}")
        print(f"Task type: {task['type'].upper()}")
        print(f"Query: {task['query'][:50]}...")
        
        try:
            # Check if provider available
            available = gateway.get_available_providers()
            if not available.get(task['provider']):
                print(f"❌ {task['provider']} not available, using default")
                continue
            
            # Switch to optimal provider
            gateway.switch_provider(task['provider'], task['model'])
            
            print(f"✅ Routing to: {task['provider']} - {task['model']}")
            
            messages = [{"role": "user", "content": task['query']}]
            
            import time
            start = time.time()
            response = gateway.chat_completion(messages)
            elapsed = time.time() - start
            
            print(f"Response: {response['content'][:100]}...")
            print(f"Time: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def example_cost_comparison():
    """Show cost differences between providers"""
    print("\n" + "=" * 60)
    print("COST COMPARISON")
    print("=" * 60)
    
    # Approximate costs per 1M tokens (input + output avg)
    costs = {
        "openai": {
            "gpt-4o": "$2.50 / 1M tokens",
            "gpt-4o-mini": "$0.15 / 1M tokens"
        },
        "anthropic": {
            "claude-3-5-sonnet": "$3.00 / 1M tokens",
            "claude-3-5-haiku": "$0.80 / 1M tokens"
        },
        "google": {
            "gemini-1.5-pro": "FREE (with limits)",
            "gemini-1.5-flash": "FREE (with limits)"
        },
        "groq": {
            "llama-3.3-70b": "FREE (with rate limits)",
            "llama-3.1-8b": "FREE (with rate limits)"
        },
        "vertex": {
            "gemini-1.5-pro": "$1.25-$5.00 / 1M tokens",
            "gemini-1.5-flash": "$0.075-$0.30 / 1M tokens"
        }
    }
    
    print("\n💰 Cost per 1M tokens (approximate):\n")
    
    for provider, models in costs.items():
        print(f"{provider.upper()}:")
        for model, cost in models.items():
            print(f"  - {model}: {cost}")
        print()
    
    print("💡 Recommendations:")
    print("- Development: Groq or Google (FREE)")
    print("- Production budget: Groq (FREE but rate limited)")
    print("- Production quality: OpenAI gpt-4o-mini or Vertex Flash")
    print("- Enterprise: Vertex AI (with SLA)")
    print("- Best reasoning: Anthropic Claude 3.5 Sonnet")


if __name__ == "__main__":
    print("\n🚀 AI GATEWAY ADVANCED EXAMPLES\n")
    
    try:
        example_groq_speed_test()
        example_compare_all_providers()
        example_model_selection()
        example_vertex_enterprise()
        example_smart_routing()
        example_cost_comparison()
        
        print("\n" + "=" * 60)
        print("✅ Completed all examples!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
