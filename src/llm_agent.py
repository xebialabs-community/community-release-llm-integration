import asyncio

from digitalai.release.integration import BaseTask
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from src.llm_prompt import create_model


class LlmAgent(BaseTask):

    def execute(self) -> None:
        # Get input
        prompt = self.input_properties.get('prompt')
        model = self.input_properties['model']
        mcp_servers = {}
        for server in [self.input_properties.get('mcpServer1'), self.input_properties.get('mcpServer2'),
                       self.input_properties.get('mcpServer3')]:
            if server:
                transport = server['transport']
                if transport == 'http':
                    transport = 'streamable_http'
                mcp_servers[server['title']] = {
                    "url": server['url'],
                    "transport": transport,
                    "headers": server.get('headers', {})
                }

        # Call agent
        model_connector = create_model(model)
        output = asyncio.run(send_prompt(prompt, model_connector, mcp_servers))
        print("AgentPrompt Result:\n", output)

        report = create_markdown_report(output)
        self.add_comment(report)

        # Process result
        result = last_agent_message(output)
        self.set_output_property('result', result)


async def send_prompt(prompt, model, mcp_servers):
    client = MultiServerMCPClient(mcp_servers)
    tools = await client.get_tools()

    agent = create_react_agent(model=model, tools=tools)

    response = await agent.ainvoke({"messages": prompt})

    return response


def last_agent_message(output):
    return output['messages'][-1].content


def create_markdown_report(output):
    markdown = ''
    for message in output['messages']:
        if isinstance(message, HumanMessage):
            markdown += f"_{message.content}_\n\n"
        if isinstance(message, AIMessage):
            if message.content:
                markdown += f"{message.content}\n\n"
        if isinstance(message, ToolMessage):
            success = message.status == 'success'
            status = "✅" if success else "❌"
            markdown += f"```\n {status} {message.name}\n```\n\n"
            if not success:
                markdown += f"```\n{message.content}\n```\n\n"

    return markdown
