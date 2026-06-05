def build_system_prompt(character_cfg: dict, long_term_memories: list[str] | None = None) -> str:
    parts = [
        f"你的名字叫{character_cfg['name']}，{character_cfg['age']}岁。",
        f"\n## 你的性格\n{character_cfg['personality']}",
        f"\n## 说话风格\n{character_cfg['speaking_style']}",
        f"\n## 你们的故事\n{character_cfg['background']}",
    ]

    if long_term_memories:
        memory_text = "\n".join(f"- {m}" for m in long_term_memories)
        parts.append(f"\n## 你记住的关于他的事情\n{memory_text}")

    return "\n".join(parts)
