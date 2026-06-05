from skills.base import Skill, SkillManager
from skills.greeting import GreetingSkill
from skills.jokes import JokeSkill
from skills.anniversary import AnniversarySkill
from skills.stickers import StickerSkill


def create_default_skills(llm, memory, config: dict) -> SkillManager:
    manager = SkillManager()
    manager.register(GreetingSkill(config))
    manager.register(JokeSkill(llm))
    manager.register(AnniversarySkill(llm, memory))
    manager.register(StickerSkill(llm))
    return manager
