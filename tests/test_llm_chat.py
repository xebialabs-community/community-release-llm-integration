import unittest
from unittest.mock import patch
from src.llm_chat import LlmChat


class TestLlmChat(unittest.TestCase):

    def test_wait_for_next_prompt(self):
        # Simulate comments being fetched one by one
        mock_comments = [
            ['one'],
            ['one', 'two'],
        ]

        def mock_get_comments():
            return mock_comments.pop(0)

        chat = LlmChat()
        with patch.object(LlmChat, 'get_comments', side_effect=mock_get_comments):
            result = chat.wait_for_next_prompt('one')
            self.assertEqual(result, 'two')

    def test_wait_for_last_response(self):
        mock_comments = [
            ['one'],
            ['one', 'two', 'three'],
        ]

        def mock_get_comments():
            return mock_comments.pop(0)

        chat = LlmChat()
        with patch.object(LlmChat, 'get_comments', side_effect=mock_get_comments):
            result = chat.wait_for_last_response('wo')
            self.assertEqual(result, (['one', 'two', 'three'], 1))
