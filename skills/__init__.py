from skills.base import Skill, SkillManager
from skills.greeting import GreetingSkill
from skills.jokes import JokeSkill
from skills.anniversary import AnniversarySkill
from skills.stickers import StickerSkill
from skills.love_message import LoveMessageSkill


def create_default_skills(llm, memory, config: dict) -> SkillManager:
    manager = SkillManager()
    manager.register(GreetingSkill(config))
    manager.register(JokeSkill(llm))
    manager.register(AnniversarySkill(llm, memory))
    manager.register(StickerSkill(llm))
    manager.register(LoveMessageSkill(config))
    return manager
