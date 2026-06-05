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
