import unittest

from src.mcp_call_tool import McpCallTool


class TestMcpCallTool(unittest.TestCase):

    @unittest.skip("No MCP server avilable for testing")
    def test_call_tool(self):
        # Given
        task = McpCallTool()
        task.input_properties = {
            'server': {
                'url': 'http://localhost:8080/',
                'transport': 'sse'
            },
            'tool': 'list_tickets',
            'input': {}
        }

        # When
        task.execute_task()

        result = task.get_output_properties()['result']
        print(result)

        # Then
        # Check if result contains 'TICKET'
        self.assertIn('TICKET', result)

    @unittest.skip("No MCP server avilable for testing")
    def test_call_tool_with_input(self):
        # Given
        task = McpCallTool()
        task.input_properties = {
            'server': {
                'url': 'http://localhost:8080/',
                'transport': 'sse'
            },
            'tool': 'list_tickets',
            'input': '{"id": "TICKET-001"}'
        }

        # When
        task.execute_task()

        result = task.get_output_properties()['result']
        print(result)

        # Then
        # Check if result contains 'TICKET'
        self.assertIn('TICKET', result)
