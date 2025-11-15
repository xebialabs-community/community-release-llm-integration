import unittest

from src.llm_prompt import LlmPrompt
import os
from dotenv import load_dotenv


class TestLlmPrompt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_gemini_prompt(self):
        # Given
        task = LlmPrompt()
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

        result = task.get_output_properties()['response']
        print(result)

        # Then
        self.assertIn('Hola', result)

    def test_dai_llm_prompt(self):
        # Given
        task = LlmPrompt()
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

        result = task.get_output_properties()['response']
        print(result)

        # Then
        self.assertIn('Hola', result)
