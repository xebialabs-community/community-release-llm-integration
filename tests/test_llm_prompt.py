import os
import unittest

from dotenv import load_dotenv

from src.llm_prompt import LlmPrompt


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

    def test_openai_prompt(self):
        # Given
        task = LlmPrompt()
        task.input_properties = {
            'prompt': 'Say hello in Spanish',
            'model': {
                'provider': 'openai',
                'url': 'https://api.openai.com/v1',
                'apiKey': os.getenv('OPENAI_API_KEY'),
                'model_id': 'gpt-5-nano'
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
                'provider': 'dai-llm',
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

    def test_local_docker_llm_prompt(self):
        # Given
        task = LlmPrompt()
        task.input_properties = {
            'prompt': 'Say hello in Spanish',
            'model': {
                'provider': 'dai-llm',
                'url': 'http://localhost:12434/engines/v1',
                'apiKey': 'none',
                'model_id': 'smollm2'
            },
        }

        # When
        task.execute_task()

        result = task.get_output_properties()['response']
        print(result)

        # Then
        self.assertIn('Hola', result)
