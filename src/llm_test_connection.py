from digitalai.release.integration import BaseTask

from src.llm_prompt import create_model, format_exception


class LlmTestConnection(BaseTask):
    def execute(self) -> None:
        result = None
        try:
            model_config = self.input_properties['server']
            model_connector = create_model(model_config)

            response = model_connector.invoke("Say OK")

            if response and response.content:
                result = {"success": True, "output": "Connection successful"}
            else:
                result = {"success": False, "output": "Connected but no response"}

        except BaseException as e:
            error_msg = f"{type(e).__name__}: {str(e)[:200]}"
            result = {"success": False, "output": error_msg}
        finally:
            if result is None:
                result = {"success": False, "output": "Unknown error occurred"}
            self.set_output_property("commandResponse", result)
