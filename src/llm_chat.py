from time import sleep, time
from typing import Dict

from digitalai.release.integration import BaseTask
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableWithMessageHistory

from src.llm_prompt import create_model, format_exception

# In-memory session store
_session_store: Dict[str, InMemoryChatMessageHistory] = {}


class LlmChat(BaseTask):

    def execute(self) -> None:
        # Get input
        model_spec = self.input_properties['model']
        if model_spec is None:
            raise ValueError("Model field cannot be empty")
        model = create_model(model_spec)
        max_idle_timeout = self.input_properties.get('maxIdleTimeout')

        # Setup chat with memory
        chat = create_chat_session(model)
        session_id = str(self.task_id)  # use task id as session identifier

        # Chat loop
        last_response = self.do_chat_loop(chat, session_id, max_idle_timeout)

        if last_response:
            # Set the output to the last response
            self.set_output_property('response', last_response.content)

            # Summarize last answer in status line
            self.set_status_line("Summarizing")
            try:
                summary = model.invoke(f"""
                Summarize the following answer in maximum 5 words. <answer>{last_response.content}</answer>""")
                self.set_status_line(summary.content)
            except Exception as e:
                root, error_details = format_exception(e)
                raise RuntimeError(f"Summarization failed - {error_details}") from root
        else:
            self.set_status_line("")

    def do_chat_loop(self, chat: Runnable, session_id: str, max_idle_timeout: int):
        answer_count = 0
        answer_marker = self.add_comment_with_marker("Welcome to the AI Chat! Type your prompts below.", answer_count)

        agent_response = None
        while True:

            # Wait for next prompt
            self.set_status_line("💬Waiting for next prompt...")
            prompt = self.wait_for_next_prompt(answer_marker, max_idle_timeout)

            # Chat ended by user or timeout
            if prompt is None:
                self.add_comment("Chat session terminated due to inactivity.")
                break
            if prompt.lower().strip() == "stop chat":
                break

            # Ask agent
            self.set_status_line("AI is thinking")
            try:
                agent_response = chat.invoke(
                    {"input": prompt},
                    config={"configurable": {"session_id": session_id}},
                )
            except Exception as e:
                root, error_details = format_exception(e)
                raise RuntimeError(f"Chat failed - {error_details}") from root

            # Send response to UI
            comment = agent_response.content
            answer_count += 1
            answer_marker = self.add_comment_with_marker(comment, answer_count)

        return agent_response

    def add_comment_with_marker(self, comment, answer_count: int) -> str:

        # Insert marker so we can locate this response in the comments later
        answer_marker = f"<!--- Answer {answer_count} --->"
        comment += "\n" + answer_marker

        # Add instructions to stop the chat
        comment += "\n\n_Type `stop chat` to end the conversation._"

        # Send comment to UI
        self.add_comment(comment)

        return answer_marker

    def wait_for_next_prompt(self, marker, max_idle_timeout: int):

        comments, last_response_index = self.wait_for_last_response(marker)

        start_time = time()
        while len(comments) <= last_response_index + 1:
            elapsed = time() - start_time
            if elapsed >= max_idle_timeout:
                return None  # Timeout
            sleep(1)
            comments = self.get_comments()

        return comments[-1]

    def wait_for_last_response(self, marker):

        while True:
            comments = self.get_comments()
            last_response_index = find_last_index_containing(comments, marker)
            if last_response_index != -1:
                return comments, last_response_index
            sleep(1)

    def get_comments(self):
        release_api_client = self.get_release_api_client()

        response = release_api_client.get(f"/api/v1/tasks/{self.task_id}")
        task = response.json()

        comments = [comment['text'] for comment in task['comments']]

        return comments


def find_last_index_containing(comments: list[str], marker: str) -> int:
    for i in range(len(comments) - 1, -1, -1):
        if marker in comments[i]:
            return i
    return -1


#
# Chat history
#

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    return _session_store.setdefault(session_id, InMemoryChatMessageHistory())


def create_chat_session(model):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("placeholder", "{history}"),
        ("human", "{input}"),
    ])
    chain = prompt | model
    return RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        history_messages_key="history",
        input_messages_key="input",
        # output_messages_key="answer",
    )
