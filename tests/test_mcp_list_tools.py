import unittest

from src.mcp_list_tools import McpListToolsTask


class TestMcpListTools(unittest.TestCase):

    @unittest.skip("No MCP server avilable for testing")
    def test_list_tools(self):
        # Given
        task = McpListToolsTask()
        task.input_properties = {
            'server': {
                'url': 'http://localhost:8080/',
                'transport': 'sse'
            },
        }

        # When
        task.execute_task()

        # Then

        # Check if result contains key 'list_tickets'
        tools = task.get_output_properties()['tools']
        self.assertIn('list_tickets', tools)

        inputSchema = task.get_output_properties()['inputSchema']
        print(inputSchema)
        self.assertIn('list_tickets', inputSchema)
