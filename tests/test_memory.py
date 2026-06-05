import pytest
import json
import os
from memory import Memory


def test_add_and_get_history(tmp_path):
    mem = Memory(str(tmp_path))
    mem.add_message("user1", "user", "你好")
    mem.add_message("user1", "assistant", "你好呀~")

    history = mem.get_history("user1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "你好呀~"


def test_history_sliding_window(tmp_path):
    mem = Memory(str(tmp_path), max_rounds=3)
    for i in range(5):
        mem.add_message("user1", "user", f"msg{i}")
        mem.add_message("user1", "assistant", f"reply{i}")

    history = mem.get_history("user1")
    assert len(history) == 6  # 3 rounds = 6 messages
    assert history[0]["content"] == "msg2"  # oldest kept


def test_long_term_memory(tmp_path):
    mem = Memory(str(tmp_path))
    mem.add_long_term_memory("用户生日是8月15日")
    mem.add_long_term_memory("用户喜欢吃辣")

    memories = mem.get_long_term_memories()
    assert len(memories) == 2
    assert "8月15日" in memories[0]


def test_persistence(tmp_path):
    mem = Memory(str(tmp_path))
    mem.add_message("user1", "user", "hello")

    # 新实例应能读取之前的数据
    mem2 = Memory(str(tmp_path))
    history = mem2.get_history("user1")
    assert len(history) == 1
    assert history[0]["content"] == "hello"
