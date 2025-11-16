from digitalai.release.integration import BaseTask

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class LlmPrompt(BaseTask):

    def execute(self) -> None:
        # Get input
        prompt = self.input_properties.get('prompt')
        model = self.input_properties['model']

        # Call agent
        self.set_status_line("AI is thinking")
        model_connector = create_model(model)
        output = model_connector.invoke(prompt)
        response = output.content

        # Send comment to the task UI
        comment = markdown_quote(prompt)
        comment += response
        self.add_comment(comment)
        self.set_status_line("")

        # Set output
        self.set_output_property('response', response)



def create_model(model):
    provider = model['provider']

    if provider == 'gemini':
        return ChatGoogleGenerativeAI(
            google_api_key=model['apiKey'],
            model=model['model_id'],
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
    if provider == 'openai':
        return ChatOpenAI(
            base_url=model['url'],
            api_key=model["apiKey"],
            model=model['model_id'],
            temperature=0.0
        )
    if provider == 'dai-llm':
        return ChatOpenAI(
            base_url=model['url'],
            api_key=model["apiKey"],
            model=model['model_id'],
            default_headers={
                'Authorization': f'Token {model["apiKey"]}',
                'X-Digitalai-AppName': 'Release',
            },
            temperature=0.0
        )
    raise ValueError(f"Provider {provider} is not supported")


def markdown_quote(text: str) -> str:
    """Wrap a multiline string into markdown quote format."""
    lines = text.split('\n')
    quoted_lines = [f"> {line}" for line in lines]
    return '\n'.join(quoted_lines) + '\n\n'
