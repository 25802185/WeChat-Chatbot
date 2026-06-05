import pytest
import yaml
import tempfile
import os


def test_load_config_reads_all_sections(tmp_path):
    cfg = {
        "character": {
            "name": "小柔",
            "age": 22,
            "personality": "test",
            "speaking_style": "test",
            "background": "test",
        },
        "llm": {
            "api_key": "sk-test",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-v4-pro",
            "max_tokens": 1024,
            "temperature": 0.85,
        },
        "user": {"wechat_id": "test_wxid"},
        "wcf": {"port": 10086},
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.dump(cfg, allow_unicode=True), encoding="utf-8")

    from config import load_config

    result = load_config(str(cfg_path))

    assert result["character"]["name"] == "小柔"
    assert result["llm"]["model"] == "deepseek-v4-pro"
    assert result["user"]["wechat_id"] == "test_wxid"
