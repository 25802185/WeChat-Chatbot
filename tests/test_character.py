import pytest
from character import build_system_prompt

def test_build_system_prompt_contains_all_parts():
    cfg = {
        "name": "小柔",
        "age": 22,
        "personality": "温柔体贴",
        "speaking_style": "口语化",
        "background": "聚会上认识的",
    }
    prompt = build_system_prompt(cfg)

    assert "小柔" in prompt
    assert "22" in prompt
    assert "温柔体贴" in prompt
    assert "口语化" in prompt
    assert "聚会上认识的" in prompt
    assert "system" not in prompt.lower()  # 不包含 meta 标签

def test_build_system_prompt_with_long_term_memory():
    cfg = {
        "name": "小柔",
        "age": 22,
        "personality": "温柔体贴",
        "speaking_style": "口语化",
        "background": "认识的",
    }
    memories = ["用户生日是8月15日", "用户喜欢吃辣"]
    prompt = build_system_prompt(cfg, memories)

    assert "8月15日" in prompt
    assert "吃辣" in prompt

def test_build_system_prompt_contains_emoji_guide():
    cfg = {
        "name": "小柔",
        "age": 22,
        "personality": "温柔体贴",
        "speaking_style": "口语化",
        "background": "认识的",
    }
    prompt = build_system_prompt(cfg)

    assert "emoji" in prompt.lower() or "Emoji" in prompt
    assert "😊" in prompt or "💕" in prompt
