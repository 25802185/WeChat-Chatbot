import time
import logging
from datetime import datetime
from skills.base import Skill

log = logging.getLogger(__name__)


class GreetingSkill(Skill):
    name = "定时问候"
    description = "每天早上发早安，晚上发晚安"

    def __init__(self, config: dict):
        self.config = config
        self.morning_hour = config.get("skills", {}).get("greeting", {}).get("morning_hour", 8)
        self.night_hour = config.get("skills", {}).get("greeting", {}).get("night_hour", 22)
        self._last_morning = ""
        self._last_night = ""

    def check_trigger(self, context: dict) -> bool:
        if context.get("type") == "command":
            text = context.get("text", "")
            return text in ["早安", "晚安"]

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if now.hour == self.morning_hour and self._last_morning != today:
            return True
        if now.hour == self.night_hour and self._last_night != today:
            return True

        return False

    def execute(self, context: dict) -> str | None:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if context.get("type") == "command":
            text = context.get("text", "")
            if text == "早安":
                self._last_morning = today
                return self._morning_message()
            if text == "晚安":
                self._last_night = today
                return self._night_message()

        if now.hour == self.morning_hour and self._last_morning != today:
            self._last_morning = today
            return self._morning_message()

        if now.hour == self.night_hour and self._last_night != today:
            self._last_night = today
            return self._night_message()

        return None

    def _morning_message(self) -> str:
        import random
        messages = [
            "早安呀~今天也要开开心心的哦 ☀️",
            "起床啦起床啦~新的一天开始了，想你了 🌅",
            "早安！记得吃早饭哦，不然我会生气的 😤",
            "早上好呀~今天天气怎么样？记得带伞哦 🌂",
            "醒了吗？我一早就想你了，快回复我嘛 💕",
        ]
        return random.choice(messages)

    def _night_message(self) -> str:
        import random
        messages = [
            "晚安~做个好梦，梦里有我哦 🌙",
            "该睡觉啦！不许熬夜，不然我生气了 😤",
            "晚安宝贝，今天辛苦了，好好休息 💤",
            "睡觉前记得想我一下下哦~晚安 🌟",
            "晚安啦~明天见，我会想你的 💕",
        ]
        return random.choice(messages)
