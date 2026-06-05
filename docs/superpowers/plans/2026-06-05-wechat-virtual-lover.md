# 微信虚拟恋人 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个接入个人微信的 AI 虚拟恋人机器人，通过 WeChatFerry 监听消息，调用 DeepSeek V4 Pro 生成回复。

**Architecture:** 单进程 Python 应用，WeChatFerry hook 微信客户端接收/发送消息，消息经过过滤后拼接人设 prompt 和对话历史，调用 DeepSeek API 获取回复。对话历史和长期记忆全部本地 JSON 存储。

**Tech Stack:** Python 3.9+, wcferry, openai (DeepSeek 兼容), pyyaml, pytest

---

## File Structure

```
talking/
├── main.py              # 入口：初始化 WCF，注册消息回调，保持运行
├── bot.py               # 核心：消息过滤、上下文拼接、调用 LLM、回复
├── llm.py               # DeepSeek API 封装（OpenAI 兼容格式）
├── character.py         # 人设 System Prompt 构建
├── memory.py            # 对话历史 + 长期记忆读写
├── config.yaml          # 配置文件（人设、API key、用户信息）
├── requirements.txt     # 依赖
├── tests/
│   ├── test_character.py
│   ├── test_memory.py
│   └── test_bot.py
└── data/                # 运行时自动创建
    ├── memory.json
    └── long_term.json
```

---

### Task 1: 项目脚手架

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml`

- [ ] **Step 1: 创建 requirements.txt**

```
wcferry
openai
pyyaml
pytest
```

- [ ] **Step 2: 创建 config.yaml**

```yaml
character:
  name: "小柔"
  age: 22
  personality: |
    你是用户的虚拟恋人。性格温柔体贴，但偶尔会撒娇、吃醋、有小脾气。
    你很在乎对方，会主动关心他的日常，记住他说过的事情。
    生气的时候虽然会哼一声，但很好哄，对方说两句好话就心软了。
    你有自己的小世界，会分享自己的心情和日常，不是只会附和。
  speaking_style: |
    说话口语化，带语气词（嘛、呀、哼、啦、呢）。
    适当使用 emoji 表达情绪，但不要每句话都用。
    偶尔发"..."表示害羞或无语。
    不会用"作为AI"之类的说法，完全沉浸在恋人角色中。
  background: |
    你们是在一次朋友聚会上认识的，聊得很投缘就在一起了。
    你喜欢追剧、吃甜食，偶尔会因为小事生闷气。

llm:
  api_key: "sk-your-key-here"
  base_url: "https://api.deepseek.com"
  model: "deepseek-v4-pro"
  max_tokens: 1024
  temperature: 0.85

user:
  wechat_id: "your_wechat_id"

wcf:
  port: 10086
```

- [ ] **Step 3: 安装依赖**

Run: `cd E:/personPro/talking && pip install -r requirements.txt`

- [ ] **Step 4: Commit**

```bash
git init
git add requirements.txt config.yaml
git commit -m "feat: project scaffolding with config"
```

---

### Task 2: config.py — 配置加载

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_config.py
import pytest
import yaml
import tempfile
import os

def test_load_config_reads_all_sections(tmp_path):
    cfg = {
        "character": {"name": "小柔", "age": 22, "personality": "test", "speaking_style": "test", "background": "test"},
        "llm": {"api_key": "sk-test", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-pro", "max_tokens": 1024, "temperature": 0.85},
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd E:/personPro/talking && python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: 实现 config.py**

```python
# config.py
import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd E:/personPro/talking && python -m pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: config loader with tests"
```

---

### Task 3: character.py — 人设 Prompt 构建

**Files:**
- Create: `character.py`
- Create: `tests/test_character.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_character.py
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd E:/personPro/talking && python -m pytest tests/test_character.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 character.py**

```python
# character.py

def build_system_prompt(character_cfg: dict, long_term_memories: list[str] | None = None) -> str:
    parts = [
        f"你的名字叫{character_cfg['name']}，{character_cfg['age']}岁。",
        f"\n## 你的性格\n{character_cfg['personality']}",
        f"\n## 说话风格\n{character_cfg['speaking_style']}",
        f"\n## 你们的故事\n{character_cfg['background']}",
    ]

    if long_term_memories:
        memory_text = "\n".join(f"- {m}" for m in long_term_memories)
        parts.append(f"\n## 你记住的关于他的事情\n{memory_text}")

    return "\n".join(parts)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd E:/personPro/talking && python -m pytest tests/test_character.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add character.py tests/test_character.py
git commit -m "feat: character prompt builder with tests"
```

---

### Task 4: memory.py — 对话历史与长期记忆

**Files:**
- Create: `memory.py`
- Create: `tests/test_memory.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_memory.py
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd E:/personPro/talking && python -m pytest tests/test_memory.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 memory.py**

```python
# memory.py
import json
import os
from datetime import datetime

class Memory:
    def __init__(self, data_dir: str = "data", max_rounds: int = 80):
        self.data_dir = data_dir
        self.max_rounds = max_rounds
        self.memory_file = os.path.join(data_dir, "memory.json")
        self.long_term_file = os.path.join(data_dir, "long_term.json")
        os.makedirs(data_dir, exist_ok=True)
        self._conversations = self._load_json(self.memory_file, {"conversations": {}})
        self._long_term = self._load_json(self.long_term_file, {"memories": []})

    def _load_json(self, path: str, default: dict) -> dict:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, path: str, data: dict):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_message(self, wxid: str, role: str, content: str):
        if wxid not in self._conversations["conversations"]:
            self._conversations["conversations"][wxid] = []

        self._conversations["conversations"][wxid].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

        # 滑动窗口：保留最近 max_rounds 轮（每轮 2 条消息）
        max_msgs = self.max_rounds * 2
        msgs = self._conversations["conversations"][wxid]
        if len(msgs) > max_msgs:
            self._conversations["conversations"][wxid] = msgs[-max_msgs:]

        self._save_json(self.memory_file, self._conversations)

    def get_history(self, wxid: str) -> list[dict]:
        return self._conversations["conversations"].get(wxid, [])

    def add_long_term_memory(self, content: str):
        self._long_term["memories"].append({
            "content": content,
            "added": datetime.now().strftime("%Y-%m-%d"),
        })
        self._save_json(self.long_term_file, self._long_term)

    def get_long_term_memories(self) -> list[str]:
        return [m["content"] for m in self._long_term["memories"]]
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd E:/personPro/talking && python -m pytest tests/test_memory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add memory.py tests/test_memory.py
git commit -m "feat: memory system with conversation history and long-term memory"
```

---

### Task 5: llm.py — DeepSeek API 封装

**Files:**
- Create: `llm.py`
- Create: `tests/test_llm.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_llm.py
import pytest
from unittest.mock import patch, MagicMock
from llm import LLM

def test_llm_chat_builds_correct_messages():
    llm = LLM(api_key="sk-test", base_url="https://api.deepseek.com", model="deepseek-v4-pro")

    with patch("llm.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd E:/personPro/talking && python -m pytest tests/test_llm.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 llm.py**

```python
# llm.py
from openai import OpenAI

class LLM:
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-v4-pro",
                 max_tokens: int = 1024, temperature: float = 0.85):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, system_prompt: str, history: list[dict]) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd E:/personPro/talking && python -m pytest tests/test_llm.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add llm.py tests/test_llm.py
git commit -m "feat: DeepSeek API wrapper with tests"
```

---

### Task 6: bot.py — 消息处理核心

**Files:**
- Create: `bot.py`
- Create: `tests/test_bot.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_bot.py
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
    with patch("bot.LLM"):
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

    reply = bot.handle_text_message("me", "你好")
    assert reply == "想你啦~"
    bot.llm.chat.assert_called_once()

def test_handle_unsupported_type():
    bot = make_bot()
    reply = bot.handle_message("me", "[图片]", msg_type=3)
    assert "图" in reply or "看" in reply
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd E:/personPro/talking && python -m pytest tests/test_bot.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 bot.py**

```python
# bot.py
from character import build_system_prompt
from memory import Memory
from llm import LLM

class Bot:
    def __init__(self, cfg: dict, data_dir: str = "data"):
        self.user_wxid = cfg["user"]["wechat_id"]
        self.character_cfg = cfg["character"]
        self.memory = Memory(data_dir)
        self.llm = LLM(
            api_key=cfg["llm"]["api_key"],
            base_url=cfg["llm"]["base_url"],
            model=cfg["llm"]["model"],
            max_tokens=cfg["llm"]["max_tokens"],
            temperature=cfg["llm"]["temperature"],
        )

    def should_handle(self, sender: str) -> bool:
        return sender == self.user_wxid

    def handle_message(self, sender: str, content: str, msg_type: int = 1) -> str:
        if not self.should_handle(sender):
            return ""

        if msg_type != 1:  # 非文字消息
            return "人家看不懂嘛~发文字给我好不好"

        return self.handle_text_message(sender, content)

    def handle_text_message(self, sender: str, content: str) -> str:
        self.memory.add_message(sender, "user", content)

        memories = self.memory.get_long_term_memories()
        system_prompt = build_system_prompt(self.character_cfg, memories)
        history = self.memory.get_history(sender)

        reply = self.llm.chat(system_prompt, history)

        self.memory.add_message(sender, "assistant", reply)
        return reply
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd E:/personPro/talking && python -m pytest tests/test_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bot.py tests/test_bot.py
git commit -m "feat: bot message handler with tests"
```

---

### Task 7: main.py — WCF 入口与消息循环

**Files:**
- Create: `main.py`

- [ ] **Step 1: 实现 main.py**

```python
# main.py
import signal
import sys
import logging
from wcferry import Wcf, WxMsg
from config import load_config
from bot import Bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def main():
    cfg = load_config()
    bot = Bot(cfg)

    wcf = Wcf()
    log.info(f"已登录，wxid: {wcf.get_self_wxid()}")
    log.info(f"虚拟恋人 [{cfg['character']['name']}] 启动成功，等待消息...")

    wcf.enable_receiving_msg()

    def shutdown(sig, frame):
        log.info("正在关闭...")
        wcf.disable_recv_msg()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    while True:
        msg: WxMsg = wcf.get_msg()
        reply = bot.handle_message(msg.sender, msg.content, msg.type)
        if reply:
            wcf.send_text(reply, msg.sender)
            log.info(f"回复 {msg.sender}: {reply[:50]}...")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: main entry point with WCF message loop"
```

---

### Task 8: 端到端验证

- [ ] **Step 1: 运行全部测试**

Run: `cd E:/personPro/talking && python -m pytest tests/ -v`
Expected: 全部 PASS

- [ ] **Step 2: 检查配置文件**

确认 `config.yaml` 中的 `api_key` 和 `wechat_id` 已填入正确值。

- [ ] **Step 3: 启动测试**

1. 打开微信 PC 客户端并登录
2. 运行 `python main.py`
3. 用另一个微信号给自己发消息
4. 确认收到虚拟恋人的回复

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete virtual lover bot"
```
