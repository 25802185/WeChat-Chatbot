import random
import logging
from skills.base import Skill

log = logging.getLogger(__name__)


class JokeSkill(Skill):
    name = "讲笑话"
    description = "主动给你发搞笑段子"

    def __init__(self, llm):
        self.llm = llm
        self._jokes = [
            "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25 🎃",
            "我跟AI说'讲个笑话'，它说'你的代码'。我：？？？",
            "一只蜗牛爬上了苹果树，树上的毛毛虫问：你来干嘛？蜗牛说：苹果还没熟，我先到 🐌",
            "为什么数学书最惨？因为它有太多问题了 📚",
            "我问风扇我丑吗，它摇了一晚上的头。开心坏了，然后发现它本来就会摇头 😂",
        ]

    def check_trigger(self, context: dict) -> bool:
        if context.get("type") == "command":
            text = context.get("text", "")
            return any(kw in text for kw in ["讲个笑话", "说个笑话", "来个笑话", "笑话"])
        return False

    def execute(self, context: dict) -> str | None:
        return random.choice(self._jokes)
