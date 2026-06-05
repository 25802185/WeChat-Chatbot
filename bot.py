from character import build_system_prompt
from memory import Memory
from llm import LLM

class Bot:
    def __init__(self, cfg: dict, data_dir: str = "data"):
        self.user_wxid = cfg["user"]["wechat_id"]
        self.character_cfg = cfg["character"]
        self.memory = Memory(data_dir)
        self.llm = LLM(
            api_key=cfg["llm"]["api_key"],
            base_url=cfg["llm"]["base_url"],
            model=cfg["llm"]["model"],
            max_tokens=cfg["llm"]["max_tokens"],
            temperature=cfg["llm"]["temperature"],
        )

    def should_handle(self, sender: str) -> bool:
        return sender == self.user_wxid

    def handle_message(self, sender: str, content: str, msg_type: int = 1) -> str:
        if not self.should_handle(sender):
            return ""

        if msg_type != 1:  # 非文字消息
            return "人家看不懂嘛~发文字给我好不好"

        return self.handle_text_message(sender, content)

    def handle_text_message(self, sender: str, content: str) -> str:
        self.memory.add_message(sender, "user", content)

        memories = self.memory.get_long_term_memories()
        system_prompt = build_system_prompt(self.character_cfg, memories)
        history = self.memory.get_history(sender)

        reply = self.llm.chat(system_prompt, history)

        self.memory.add_message(sender, "assistant", reply)
        return reply
