from character import build_system_prompt
from memory import Memory
from llm import LLM
from emotion import detect_emotion
from character_mood import CharacterMood
from relationship import Relationship


class Bot:
    def __init__(self, cfg: dict, data_dir: str = "data"):
        self.cfg = cfg
        self.character_cfg = cfg["character"]
        weixin_cfg = cfg.get("weixin", {})
        data_dir = weixin_cfg.get("data_dir", data_dir)
        self.memory = Memory(data_dir)
        self.mood = CharacterMood(data_dir)
        self.relationship = Relationship(data_dir)
        self.llm = LLM(
            api_key=cfg["llm"]["api_key"],
            base_url=cfg["llm"]["base_url"],
            model=cfg["llm"]["model"],
            max_tokens=cfg["llm"]["max_tokens"],
            temperature=cfg["llm"]["temperature"],
        )

    def reload_config(self, cfg: dict):
        self.cfg = cfg
        self.character_cfg = cfg["character"]

    def handle_text_message(self, sender: str, content: str) -> str:
        self.memory.add_message(sender, "user", content)

        self.mood.update(content)
        memories = self.memory.get_organized_memories()
        emotion = detect_emotion(content)
        mood_prompt = self.mood.get_mood_prompt()
        relationship_prompt = self.relationship.get_stage_prompt()
        system_prompt = build_system_prompt(self.character_cfg, memories, emotion, mood_prompt, relationship_prompt)
        history = self.memory.get_history(sender)

        reply = self.llm.chat(system_prompt, history)

        if reply is None:
            return "我现在有点不舒服，等会儿再聊好不好~"

        reply = self._post_process_emoji(reply, emotion, self.mood.mood)
        self.memory.add_message(sender, "assistant", reply)
        self._maybe_extract_memory(history, reply)
        return reply

    def _post_process_emoji(self, reply: str, emotion: str, mood: str) -> str:
        """确保emoji风格一致，如果LLM没有加emoji则根据情绪补充"""
        from emotion import has_emoji, get_emoji_for_emotion

        if has_emoji(reply):
            return reply

        # 根据用户情绪补充emoji
        emoji = get_emoji_for_emotion(emotion)
        if emoji:
            return reply + emoji

        # 根据角色心情补充emoji
        if mood in ("开心", "害羞", "想念"):
            emoji = get_emoji_for_emotion(mood)
            if emoji:
                return reply + emoji

        return reply

    def _maybe_extract_memory(self, history: list[dict], latest_reply: str):
        if len(history) % 10 != 0:
            return

        recent = history[-10:]
        conversation = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
        extract_prompt = (
            '从以下对话中提取关于用户的重要个人信息。按以下分类提取，每条信息一行，格式为"分类: 内容"。\n\n'
            '分类说明：\n'
            '- 喜好：用户喜欢的食物、音乐、电影、运动、颜色等\n'
            '- 习惯：用户的日常习惯、作息、生活方式等\n'
            '- 事件：用户提到的重要事件、经历、计划等\n'
            '- 承诺：用户做出的承诺或约定（如"下次带你去"、"答应你"等）\n'
            '- 其他：生日、家人、工作等其他重要信息\n\n'
            '如果没有值得记录的信息，回复"无"。\n\n'
            f'{conversation}'
        )
        result = self.llm.chat(extract_prompt, [])
        if result and "无" not in result:
            for line in result.strip().split("\n"):
                line = line.strip().lstrip("- ")
                if not line:
                    continue
                # 解析分类
                category = "其他"
                for cat in ["喜好", "习惯", "事件", "承诺"]:
                    if line.startswith(f"{cat}:"):
                        category = cat
                        line = line[len(cat)+1:].strip()
                        break
                self.memory.add_long_term_memory(line, category)
