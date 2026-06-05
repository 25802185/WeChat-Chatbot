import time
import logging

log = logging.getLogger(__name__)


class Skill:
    name: str = "base"
    description: str = ""

    def check_trigger(self, context: dict) -> bool:
        return False

    def execute(self, context: dict) -> str | None:
        return None


class SkillManager:
    def __init__(self):
        self.skills: list[Skill] = []
        self.last_check: dict[str, float] = {}
        self.last_message_time: float = 0

    def register(self, skill: Skill):
        self.skills.append(skill)
        log.info(f"已加载技能: {skill.name}")

    def check_and_execute(self, context: dict) -> list[str]:
        results = []
        for skill in self.skills:
            try:
                if skill.check_trigger(context):
                    reply = skill.execute(context)
                    if reply:
                        results.append(reply)
                        self.last_check[skill.name] = time.time()
            except Exception as e:
                log.error(f"技能 {skill.name} 执行失败: {e}")
        return results

    def check_command(self, text: str) -> str | None:
        context = {"type": "command", "text": text}
        for skill in self.skills:
            try:
                if skill.check_trigger(context):
                    return skill.execute(context)
            except Exception as e:
                log.error(f"技能 {skill.name} 执行失败: {e}")
        return None
