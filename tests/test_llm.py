import pytest
from unittest.mock import patch, MagicMock
from llm import LLM


def test_llm_chat_builds_correct_messages():
    with patch("llm.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        llm = LLM(api_key="sk-test", base_url="https://api.deepseek.com", model="deepseek-v4-pro")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "你好呀~"
        mock_client.chat.completions.create.return_value = mock_response

        result = llm.chat("你是小柔", [{"role": "user", "content": "你好"}])

        assert result == "你好呀~"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "deepseek-v4-pro"
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "你是小柔"
        assert messages[1]["role"] == "user"