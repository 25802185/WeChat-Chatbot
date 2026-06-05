import pytest
from unittest.mock import MagicMock, patch
from bot import Bot


def make_bot():
    cfg = {
        "character": {
            "name": "小柔", "age": 22,
            "personality": "温柔体贴", "speaking_style": "口语化",
            "background": "认识的",
        },
        "llm": {"api_key": "sk-test", "base_url": "https://api.deepseek.com",
                "model": "deepseek-v4-pro", "max_tokens": 1024, "temperature": 0.85},
        "weixin": {"data_dir": "data"},
    }
    with patch("bot.LLM"), patch("bot.Memory"):
        bot = Bot(cfg)
    return bot


def test_handle_text_message_returns_reply():
    bot = make_bot()
    bot.llm = MagicMock()
    bot.llm.chat.return_value = "想你啦~"
    bot.memory = MagicMock()
    bot.memory.get_long_term_memories.return_value = []
    bot.memory.get_history.return_value = []

    with patch.object(bot, "_maybe_extract_memory"):
        reply = bot.handle_text_message("user1", "你好")

    assert reply == "想你啦~"


def test_handle_text_message_llm_failure():
    bot = make_bot()
    bot.llm = MagicMock()
    bot.llm.chat.return_value = None
    bot.memory = MagicMock()
    bot.memory.get_long_term_memories.return_value = []
    bot.memory.get_history.return_value = []

    reply = bot.handle_text_message("user1", "你好")
    assert "不舒服" in reply


def test_post_process_emoji_adds_when_missing():
    bot = make_bot()
    result = bot._post_process_emoji("想你啦", "撒娇", "正常")
    assert "💕" in result or "🥺" in result or "😘" in result or "🥰" in result


def test_post_process_emoji_does_not_add_when_present():
    bot = make_bot()
    result = bot._post_process_emoji("想你啦😊", "撒娇", "正常")
    assert result == "想你啦😊"


def test_post_process_emoji_neutral_no_add():
    bot = make_bot()
    result = bot._post_process_emoji("今天天气不错", "neutral", "正常")
    assert result == "今天天气不错"
