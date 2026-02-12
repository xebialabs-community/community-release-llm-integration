from digitalai.release.integration import BaseTask

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class LlmPrompt(BaseTask):

    def execute(self) -> None:
        # Get input
        prompt = self.input_properties.get('prompt')
        if prompt is None:
            raise ValueError("Prompt field cannot be empty")
        model = self.input_properties.get('model')
        if model is None:
            raise ValueError("Model field cannot be empty")
        # Call agent
        self.set_status_line("AI is thinking")
        model_connector = create_model(model)
        try:
            output = model_connector.invoke(prompt)
            response = output.content
        except Exception as e:
            root, error_details = format_exception(e)
            raise RuntimeError(f"LLM invocation failed - {error_details}") from root

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


def unwrap_exception(exc: BaseException) -> BaseException:
    if isinstance(exc, BaseExceptionGroup) and exc.exceptions:
        return unwrap_exception(exc.exceptions[0])

    if exc.__cause__:
        return unwrap_exception(exc.__cause__)

    if exc.__context__:
        return unwrap_exception(exc.__context__)

    return exc

def format_exception(exc: BaseException) -> tuple[BaseException, str]:
    """Get the root exception and a formatted error message, handling empty messages."""
    root = unwrap_exception(exc)
    error_msg = str(root).strip() if str(root).strip() else "No error details provided"
    formatted = f"{type(root).__name__}: {error_msg}"
    return root, formatted
