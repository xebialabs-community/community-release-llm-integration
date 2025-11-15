import asyncio

from digitalai.release.integration import BaseTask
from fastmcp import Client

from src.mcp_call_tool import create_transport
from src.mcp_list_tools import list_tools


class McpToolLookupScript(BaseTask):
    """
        Testing connection to the remote server
    """

    def execute(self) -> None:

        try:
            # Process input
            server = self.input_properties["_ci"]['server']
            if server is None:
                raise ValueError("Server field cannot be empty")

            # Make request
            transport = create_transport(server)
            client = Client(transport)
            output = asyncio.run(list_tools(client))

            # Process result
            result = to_tool_result(output)
        except Exception as e:
            result = []

        self.set_output_property("commandResponse", result)


def to_tool_result(output):
    # Build a list of dicts with 'label' and 'value' keys
    return [{'label': tool.name, 'value': tool.name} for tool in output]
