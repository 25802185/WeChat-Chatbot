import json
import os
import time
import logging
from datetime import datetime

log = logging.getLogger(__name__)

MOODS = ["正常", "开心", "害羞", "吃醋", "委屈", "想念"]

MOOD_KEYWORDS = {
    "开心": ["开心", "高兴", "太好了", "棒", "厉害", "爽", "666", "哈哈"],
    "害羞": ["想你", "爱你", "宝贝", "亲亲", "抱抱", "喜欢你", "好爱", "最美", "最可爱"],
    "吃醋": ["她", "前女友", "女同事", "女同学", "美女", "别的女生", "那个女生"],
}

APOLOGY_KEYWORDS = ["对不起", "抱歉", "我错了", "下次不会", "别生气", "哄你", "别哭"]
PRAISE_KEYWORDS = ["好看", "漂亮", "可爱", "美", "好看", "好看", "好看"]


class CharacterMood:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.mood_file = os.path.join(data_dir, "mood.json")
        os.makedirs(data_dir, exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(self.mood_file):
            try:
                with open(self.mood_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.mood = data.get("mood", "正常")
                        self.last_interaction = data.get("last_interaction", 0)
                        self.mood_intensity = data.get("mood_intensity", 0)
                        return
            except Exception:
                pass
        self.mood = "正常"
        self.last_interaction = time.time()
        self.mood_intensity = 0

    def _save(self):
        data = {
            "mood": self.mood,
            "last_interaction": self.last_interaction,
            "mood_intensity": self.mood_intensity,
        }
        with open(self.mood_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update(self, user_message: str):
        now = time.time()
        hours_since_last = (now - self.last_interaction) / 3600

        new_mood = None

        for kw in MOOD_KEYWORDS["害羞"]:
            if kw in user_message:
                new_mood = "害羞"
                self.mood_intensity = min(10, self.mood_intensity + 2)
                break

        if not new_mood:
            for kw in MOOD_KEYWORDS["吃醋"]:
                if kw in user_message:
                    new_mood = "吃醋"
                    self.mood_intensity = min(10, self.mood_intensity + 3)
                    break

        if not new_mood:
            for kw in APOLOGY_KEYWORDS:
                if kw in user_message:
                    if self.mood in ("吃醋", "委屈"):
                        new_mood = "正常"
                        self.mood_intensity = max(0, self.mood_intensity - 3)
                    break

        if not new_mood:
            for kw in PRAISE_KEYWORDS:
                if kw in user_message:
                    new_mood = "害羞"
                    self.mood_intensity = min(10, self.mood_intensity + 1)
                    break

        if not new_mood and hours_since_last > 6:
            if self.mood != "委屈":
                new_mood = "想念"
                self.mood_intensity = min(10, int(hours_since_last / 2))

        if new_mood:
            self.mood = new_mood

        self.last_interaction = now
        self.mood_intensity = max(0, self.mood_intensity - 1)
        self._save()

    def get_mood_prompt(self) -> str:
        if self.mood == "正常":
            return ""

        mood_behaviors = {
            "开心": "你现在心情很好，语气轻快，可以多用emoji",
            "害羞": "你现在有点害羞，回复简短，用...或省略号",
            "吃醋": "你现在有点吃醋，语气淡淡的，回复简短",
            "委屈": "你现在有点委屈，语气低落，回复简短",
            "想念": "你现在想他，可以直接说想他了或问他在干嘛",
        }

        behavior = mood_behaviors.get(self.mood, "")
        if not behavior:
            return ""

        return f"\n## 你现在的心情\n{behavior}。"
