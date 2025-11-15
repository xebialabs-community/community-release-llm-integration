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
        comment = f"_{prompt}_\n\n"
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
            default_headers={
                'Authorization': f'Token {model["apiKey"]}',
                'X-Digitalai-AppName': 'Release',
            },
            temperature=0.0
        )
    raise ValueError(f"Provider {provider} is not supported")
