import json
import os
import logging
from datetime import datetime
from skills.base import Skill

log = logging.getLogger(__name__)


class AnniversarySkill(Skill):
    name = "纪念日提醒"
    description = "记住特殊日子并主动提醒"

    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
        self._anniversaries: list[dict] = []
        self._notified_today: set[str] = set()
        self._load()

    def _load(self):
        path = os.path.join(self.memory.data_dir, "anniversaries.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._anniversaries = json.load(f)
            except Exception:
                self._anniversaries = []

    def _save(self):
        path = os.path.join(self.memory.data_dir, "anniversaries.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._anniversaries, f, ensure_ascii=False, indent=2)

    def add(self, name: str, date: str):
        self._anniversaries.append({"name": name, "date": date})
        self._save()

    def check_trigger(self, context: dict) -> bool:
        if context.get("type") == "command":
            text = context.get("text", "")
            if "纪念日" in text or "生日" in text:
                return True
            return False

        today = datetime.now().strftime("%m-%d")
        for ann in self._anniversaries:
            ann_date = ann.get("date", "")
            if len(ann_date) >= 5 and ann_date[-5:] == today:
                if ann["name"] not in self._notified_today:
                    return True
        return False

    def execute(self, context: dict) -> str | None:
        if context.get("type") == "command":
            text = context.get("text", "")
            return self._handle_command(text)

        today = datetime.now().strftime("%m-%d")
        for ann in self._anniversaries:
            ann_date = ann.get("date", "")
            if len(ann_date) >= 5 and ann_date[-5:] == today:
                if ann["name"] not in self._notified_today:
                    self._notified_today.add(ann["name"])
                    return self._reminder_message(ann)
        return None

    def _handle_command(self, text: str) -> str:
        if "添加" in text or "新增" in text:
            return "告诉我纪念日的名称和日期吧，比如：添加纪念日 恋爱纪念日 2025-01-15"

        if "列表" in text or "查看" in text or "有哪些" in text:
            if not self._anniversaries:
                return "还没有记录任何纪念日哦~"
            lines = ["已记录的纪念日："]
            for ann in self._anniversaries:
                lines.append(f"  {ann['name']}: {ann['date']}")
            return "\n".join(lines)

        if not self._anniversaries:
            return "还没有记录任何纪念日哦~告诉我重要的日子吧！"
        return None

    def _reminder_message(self, ann: dict) -> str:
        name = ann["name"]
        date = ann["date"]
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            year = datetime.now().year - d.year
            if year > 0:
                return f"今天是{name} {year}周年啦！要记得庆祝哦 💝"
        except Exception:
            pass
        return f"今天是{name}哦！是个特别的日子 💝"
