import os
import unittest
from dotenv import load_dotenv
from src.llm_agent import LlmAgent


class TestAgentPrompt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_agent_prompt_echo(self):
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

    def test_agent_prompt_with_digital_ai(self):
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
    def test_with_release_mcp(self):
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

    def test_ticket_reorder_mcp(self):
        # Given
        task = LlmAgent()
        task.input_properties = {
            'prompt': """Write a Python script that will find the highest priority tickets and move 
              them to the top of the backlog. Assume that the script can call an MCP tool with 
              the the function call mcp_tool_call(server, tool, input) """,
            'model': {
                'provider': 'openai',
                'url': 'https://api.staging.digital.ai/llm',
                'apiKey': os.getenv('DAI_LLM_API_KEY'),
                'model_id': 'amazon.nova-micro-v1:0'
                # 'model_id': 'anthropic.claude-sonnet-4-20250514-v1:0'
            },
            'mcpServer1': {
                'title': 'Ticket MCP',
                'url': 'http://host.docker.internal:8080',
                'transport': 'sse',
            }
        }

        # When
        task.execute_task()
        result = task.get_output_properties()['result']
        print(result)

        # Then
