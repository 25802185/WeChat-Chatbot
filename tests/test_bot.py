import pytest
from unittest.mock import MagicMock, patch
from bot import Bot

def make_bot(user_wxid="test_user"):
    cfg = {
        "character": {
            "name": "小柔", "age": 22,
            "personality": "温柔体贴", "speaking_style": "口语化",
            "background": "认识的",
        },
        "llm": {"api_key": "sk-test", "base_url": "https://api.deepseek.com",
                "model": "deepseek-v4-pro", "max_tokens": 1024, "temperature": 0.85},
        "user": {"wechat_id": user_wxid},
    }
    with patch("bot.LLM"), patch("bot.Memory"):
        bot = Bot(cfg, data_dir=":memory:")
    return bot

def test_should_handle_ignores_other_users():
    bot = Bot.__new__(Bot)
    bot.user_wxid = "me"
    assert bot.should_handle("other_user") is False

def test_should_handle_accepts_self():
    bot = Bot.__new__(Bot)
    bot.user_wxid = "me"
    assert bot.should_handle("me") is True

def test_handle_text_message_returns_reply():
    bot = make_bot("me")
    bot.llm = MagicMock()
    bot.llm.chat.return_value = "想你啦~"
    bot.memory = MagicMock()
    bot.memory.get_long_term_memories.return_value = []
    bot.memory.get_history.return_value = []

    with patch.object(bot, "_maybe_extract_memory"):
        reply = bot.handle_text_message("me", "你好")

    assert reply == "想你啦~"

def test_handle_text_message_llm_failure():
    bot = make_bot("me")
    bot.llm = MagicMock()
    bot.llm.chat.return_value = None
    bot.memory = MagicMock()
    bot.memory.get_long_term_memories.return_value = []
    bot.memory.get_history.return_value = []

    reply = bot.handle_text_message("me", "你好")
    assert "不舒服" in reply

def test_handle_unsupported_type():
    bot = make_bot("me")
    reply = bot.handle_message("me", "[图片]", msg_type=3)
    assert "图" in reply or "看" in reply
