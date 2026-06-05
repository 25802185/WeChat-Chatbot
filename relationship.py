import json
import os
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class Relationship:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.relationship_file = os.path.join(data_dir, "relationship.json")
        os.makedirs(data_dir, exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(self.relationship_file):
            try:
                with open(self.relationship_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.start_date = data.get("start_date", "")
                        self.stage = data.get("stage", "初识期")
                        self.milestones = data.get("milestones", [])
                        return
            except Exception:
                pass
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        self.stage = "初识期"
        self.milestones = []
        self._save()

    def _save(self):
        data = {
            "start_date": self.start_date,
            "stage": self.stage,
            "milestones": self.milestones,
        }
        with open(self.relationship_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_days(self) -> int:
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            now = datetime.now()
            return (now - start).days
        except Exception:
            return 0

    def get_stage(self) -> str:
        days = self.get_days()
        if days < 7:
            self.stage = "初识期"
        elif days < 30:
            self.stage = "热恋期"
        else:
            self.stage = "稳定期"
        self._save()
        return self.stage

    def check_milestone(self) -> str | None:
        days = self.get_days()
        milestones = [7, 30, 100, 200, 365, 500, 730, 1000]

        for m in milestones:
            if days == m and m not in self.milestones:
                self.milestones.append(m)
                self._save()
                return f"今天是我们在一起{m}天纪念日！"

        if days > 0 and days % 365 == 0 and days not in self.milestones:
            self.milestones.append(days)
            self._save()
            years = days // 365
            return f"今天是我们在一起{years}周年纪念日！"

        return None

    def get_stage_prompt(self) -> str:
        days = self.get_days()
        stage = self.get_stage()

        stage_behaviors = {
            "初识期": f"你们刚在一起{days}天，聊天自然一点，不要太粘人。",
            "热恋期": f"你们在一起{days}天了，可以适当撒娇说想他。",
            "稳定期": f"你们在一起{days}天了，像平时一样自然聊天就好。",
        }

        behavior = stage_behaviors.get(stage, "")

        milestone_msg = self.check_milestone()
        if milestone_msg:
            behavior += f"\n重要提醒：{milestone_msg}"

        return f"\n## 你们的关系\n{behavior}" if behavior else ""
