import os
import unittest
from dotenv import load_dotenv
from src.llm_agent import LlmAgent


class TestLlmAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_gemini_agent_prompt(self):
        # Given
        task = LlmAgent()
        task.input_properties = {
            'prompt': 'Say hello in Spanish',
            'model': {
                'provider': 'gemini',
                'apiKey': os.getenv('GEMINI_API_KEY'),
                'model_id': 'gemini-2.5-flash-lite'
            },
        }

        # When
        task.execute_task()
        result = task.get_output_properties()['result']
        print(result)

        # Then
        self.assertIn('Hola', result)

    def test_dai_llm_agent_prompt(self):
        # Given
        task = LlmAgent()
        task.input_properties = {
            'prompt': 'Say hello in Spanish',
            'model': {
                'provider': 'openai',
                'url': 'https://api.staging.digital.ai/llm',
                'apiKey': os.getenv('DAI_LLM_API_KEY'),
                'model_id': 'amazon.nova-micro-v1:0'
            },
        }

        # When
        task.execute_task()
        result = task.get_output_properties()['result']
        print(result)

        # Then
        self.assertIn('Hola', result)

    @unittest.skip("Release token expired")
    def test_gemini_agent_with_release_mcp(self):
        # Given
        task = LlmAgent()
        task.input_properties = {
            'prompt': 'What is the latest failed release',
            'model': {
                'provider': 'gemini',
                'apiKey': os.getenv('GEMINI_API_KEY'),
                'model_id': 'gemini-2.5-flash'
            },
            'mcpServer1': {
                'title': 'Release MCP',
                'url': 'http://localhost:8000/mcp',
                'transport': 'http',
            }
        }

        # When
        task.execute_task()
        result = task.get_output_properties()['result']
        print(result)

        # Then
        # self.assertIn('Hola', result)