"""
Unit tests cho AI Gateway
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai_gateway.config import AIConfig
from app.ai_gateway.base_provider import BaseAIProvider


class TestAIConfig(unittest.TestCase):
    """Test AIConfig class"""
    
    def test_config_from_dict(self):
        """Test tạo config từ dict"""
        config_dict = {
            "provider": "openai",
            "model": "gpt-4",
            "api_keys": {
                "openai": "test-key"
            }
        }
        
        config = AIConfig(config_dict)
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.api_keys["openai"], "test-key")
    
    def test_config_validation(self):
        """Test validation"""
        config = AIConfig({
            "provider": "openai",
            "api_keys": {"openai": "test-key"},
            "model": "gpt-4"
        })
        
        self.assertTrue(config.validate())
    
    def test_config_validation_fails_no_api_key(self):
        """Test validation fails khi không có API key"""
        config = AIConfig({
            "provider": "openai",
            "api_keys": {},
            "model": "gpt-4"
        })
        
        with self.assertRaises(ValueError):
            config.validate()
    
    def test_switch_provider(self):
        """Test switch provider"""
        config = AIConfig({
            "provider": "openai",
            "api_keys": {"openai": "test-key", "anthropic": "test-key-2"},
            "model": "gpt-4"
        })
        
        config.switch_provider("anthropic")
        self.assertEqual(config.provider, "anthropic")
        self.assertEqual(config.model, "claude-3-5-sonnet-20241022")
    
    def test_get_available_providers(self):
        """Test get available providers"""
        config = AIConfig({
            "provider": "openai",
            "api_keys": {
                "openai": "test-key",
                "anthropic": None,
                "google": "test-key-google"
            }
        })
        
        available = config.get_available_providers()
        self.assertTrue(available["openai"])
        self.assertFalse(available["anthropic"])
        self.assertTrue(available["google"])


class TestBaseProvider(unittest.TestCase):
    """Test BaseAIProvider abstract class"""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test không thể tạo instance của abstract class"""
        with self.assertRaises(TypeError):
            BaseAIProvider(api_key="test", model="test")


class MockProvider(BaseAIProvider):
    """Mock provider for testing"""
    
    def chat_completion(self, messages, tools=None, tool_choice="auto", **kwargs):
        return {
            "content": "Mock response",
            "tool_calls": [],
            "finish_reason": "stop"
        }
    
    def get_provider_name(self):
        return "mock"


class TestMockProvider(unittest.TestCase):
    """Test với mock provider"""
    
    def test_mock_provider_creation(self):
        """Test tạo mock provider"""
        provider = MockProvider(api_key="test-key", model="test-model")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "test-model")
        self.assertEqual(provider.get_provider_name(), "mock")
    
    def test_mock_provider_chat(self):
        """Test chat completion với mock provider"""
        provider = MockProvider(api_key="test-key", model="test-model")
        
        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat_completion(messages)
        
        self.assertEqual(response["content"], "Mock response")
        self.assertEqual(response["finish_reason"], "stop")


if __name__ == "__main__":
    print("Running AI Gateway Unit Tests...\n")
    unittest.main(verbosity=2)
