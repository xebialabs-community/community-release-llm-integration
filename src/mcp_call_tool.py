from digitalai.release.integration import BaseTask

import asyncio
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport, SSETransport, ClientTransport
from fastmcp.client.client import CallToolResult
import json
from mcp.types import TextContent


class McpCallTool(BaseTask):

    def execute(self) -> None:
        # Process input
        server = self.input_properties['server']
        if server is None:
            raise ValueError("Server field cannot be empty")
        tool = self.input_properties['tool']
        tool_input = self.input_properties['input']
        if not tool_input:
            tool_input = {}
        else:
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON for input")

        # print("Tool Input:\n", tool_input)

        transport = create_transport(server)

        # Make request
        client = Client(transport)
        output = asyncio.run(call_tool(client, tool, tool_input))

        result = extract_result_text(output)

        # Process result
        self.set_output_property('result', result)


def create_transport(server) -> ClientTransport:
    server_url = server['url'].strip("/")
    if server['transport'] == 'sse':
        transport = SSETransport(
            url=server_url,
        )
    else:
        transport = StreamableHttpTransport(
            url=server_url,
        )
    transport.url = server_url
    transport.headers = server['headers'] if 'headers' in server else {}
    return transport


# Async method to call tool
async def call_tool(client, tool, input):
    async with client:
        return await client.call_tool(tool, input)


def extract_result_text(result: CallToolResult) -> str:
    """
    Flatten CallToolResult into a single string.
    Preference order:
    1. structured_content (if dict/list) -> JSON-ish repr
    2. data (if primitive)
    3. concatenated text content
    """
    # structured_content may already be serializable
    if result.structured_content is not None:
        return str(result.structured_content)
    if result.data is not None:
        return str(result.data)

    parts = []
    for c in result.content or []:
        if isinstance(c, TextContent) and c.text:
            parts.append(c.text)
        else:
            parts.append(str(c))
    return "\n\n".join(parts).strip()
