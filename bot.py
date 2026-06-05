from character import build_system_prompt
from memory import Memory
from llm import LLM


class Bot:
    def __init__(self, cfg: dict, data_dir: str = "data"):
        self.character_cfg = cfg["character"]
        weixin_cfg = cfg.get("weixin", {})
        self.memory = Memory(weixin_cfg.get("data_dir", data_dir))
        self.llm = LLM(
            api_key=cfg["llm"]["api_key"],
            base_url=cfg["llm"]["base_url"],
            model=cfg["llm"]["model"],
            max_tokens=cfg["llm"]["max_tokens"],
            temperature=cfg["llm"]["temperature"],
        )

    def handle_text_message(self, sender: str, content: str) -> str:
        self.memory.add_message(sender, "user", content)

        memories = self.memory.get_long_term_memories()
        system_prompt = build_system_prompt(self.character_cfg, memories)
        history = self.memory.get_history(sender)

        reply = self.llm.chat(system_prompt, history)

        if reply is None:
            return "我现在有点不舒服，等会儿再聊好不好~"

        self.memory.add_message(sender, "assistant", reply)
        self._maybe_extract_memory(history, reply)
        return reply

    def _maybe_extract_memory(self, history: list[dict], latest_reply: str):
        if len(history) % 20 != 0:
            return

        recent = history[-10:]
        conversation = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
        extract_prompt = (
            '从以下对话中提取关于用户的重要个人信息（生日、喜好、习惯、重要事件等）。'
            '每条信息一行，格式为简短陈述句。如果没有值得记录的信息，回复"无"。\n\n'
            f'{conversation}'
        )
        result = self.llm.chat(extract_prompt, [])
        if result and "无" not in result:
            for line in result.strip().split("\n"):
                line = line.strip().lstrip("- ")
                if line:
                    self.memory.add_long_term_memory(line)
