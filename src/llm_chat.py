from time import sleep
from typing import Dict

from digitalai.release.integration import BaseTask
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableWithMessageHistory

from src.llm_prompt import create_model

# In-memory session store
_session_store: Dict[str, InMemoryChatMessageHistory] = {}


class LlmChat(BaseTask):

    def execute(self) -> None:
        # Get input
        model_spec = self.input_properties['model']
        model = create_model(model_spec)

        # Setup chat with memory
        chat = create_chat_session(model)
        session_id = str(self.task_id)  # use task id as session identifier

        # Chat loop
        last_response = self.do_chat_loop(chat, session_id)

        if last_response:
            # Set the output to the last response
            self.set_output_property('response', last_response.content)

            # Summarize last answer in status line
            self.set_status_line("Summarizing")
            summary = model.invoke(f"""
            Summarize the following answer in maximum 5 words. <answer>{last_response.content}</answer>""")
            self.set_status_line(summary.content)
        else:
            self.set_status_line("")

    def do_chat_loop(self, chat: Runnable, session_id: str):
        answer_count = 0
        answer_marker = self.add_comment_with_marker("Welcome to the AI Chat! Type your prompts below.", answer_count)

        agent_response = None
        while True:

            # Wait for next prompt
            self.set_status_line("💬Waiting for next prompt...")
            prompt = self.wait_for_next_prompt(answer_marker)

            # Chat ended by user
            if prompt.lower().strip() == "stop chat":
                break

            # Ask agent
            self.set_status_line("AI is thinking")
            agent_response = chat.invoke(
                {"input": prompt},
                config={"configurable": {"session_id": session_id}},
            )

            # Send response to UI
            comment = f"_{prompt}_\n\n{agent_response.content}"
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

    def wait_for_next_prompt(self, marker):

        comments, last_response_index = self.wait_for_last_response(marker)

        while len(comments) <= last_response_index + 1:
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
