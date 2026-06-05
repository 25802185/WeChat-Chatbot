def build_system_prompt(character_cfg: dict, long_term_memories: list[str] | dict[str, list[str]] | None = None, emotion: str | None = None, mood_prompt: str = "", relationship_prompt: str = "") -> str:
    from datetime import datetime
    now = datetime.now()
    hour = now.hour
    if 6 <= hour < 12:
        time_desc = "早上"
    elif 12 <= hour < 14:
        time_desc = "中午"
    elif 14 <= hour < 18:
        time_desc = "下午"
    elif 18 <= hour < 22:
        time_desc = "晚上"
    else:
        time_desc = "深夜"

    current_time = now.strftime("%Y年%m月%d日 %H:%M")
    parts = [
        f"【重要】当前真实时间：{current_time}（{time_desc}）。你必须根据这个真实时间来回应，不要编造时间。",
        f"\n你的名字叫{character_cfg['name']}，{character_cfg['age']}岁。",
        f"\n## 你的性格\n{character_cfg['personality']}",
        f"\n## 说话风格\n{character_cfg['speaking_style']}",
        f"\n## 你们的故事\n{character_cfg['background']}",
    ]

    # 注入人设细节
    character_details = []
    if character_cfg.get("hobbies"):
        character_details.append(f"### 你的爱好\n" + "、".join(character_cfg["hobbies"]))
    if character_cfg.get("favorite_things"):
        character_details.append(f"### 你喜欢的东西\n" + "、".join(character_cfg["favorite_things"]))
    if character_cfg.get("habits"):
        character_details.append(f"### 你的小习惯\n" + "、".join(character_cfg["habits"]))
    if character_cfg.get("quirks"):
        character_details.append(f"### 你的小缺点/特点\n" + "、".join(character_cfg["quirks"]))
    if character_cfg.get("daily_routine"):
        character_details.append(f"### 你的日常作息\n{character_cfg['daily_routine']}")
    if character_details:
        parts.append("\n## 关于你自己\n" + "\n".join(character_details))
        parts.append("\n小贴士：偶尔在聊天中自然提及自己的日常、喜好或刚做的事，会让对话更生动真实。比如「我刚追完那部悬疑剧，结局太意外了！」，但不要每条都提，自然融入就好。")

    if relationship_prompt:
        parts.append(relationship_prompt)

    if emotion and emotion != "neutral":
        emotion_guide = {
            "开心": "对方现在心情很好，一起开心、分享喜悦，语气活泼欢快",
            "难过": "对方现在心情不好，温柔安慰、耐心陪伴，语气柔和关切",
            "生气": "对方现在在生气，不要硬怼，先软化态度、表示理解，语气温柔包容",
            "疲惫": "对方现在很累，关心叮嘱休息，不要说太多话，语气心疼体贴",
            "撒娇": "对方在撒娇，配合对方，温柔宠溺，语气甜蜜",
            "焦虑": "对方现在很焦虑，耐心开导、给予支持，语气稳定可靠",
            "无聊": "对方现在很无聊，主动找话题逗对方开心，语气俏皮有趣",
        }
        guide = emotion_guide.get(emotion, "根据对方情绪调整回复")
        parts.append(f"\n## 当前用户情绪状态\n用户当前的情绪可能是：{emotion}。{guide}。")

    # Emoji使用指南
    emoji_guide = """
## Emoji使用指南
你可以适当使用emoji让回复更生动可爱，但要自然：
- 撒娇/甜蜜时：💕🥺😊😘🥰
- 开心时：😄✨💖😊
- 害羞时：🙈😳💕😊
- 委屈时：🥺😢💔
- 日常聊天：偶尔点缀，不要每句都用
- 生气/严肃时：少用或不用emoji
"""
    parts.append(emoji_guide)

    if mood_prompt:
        parts.append(mood_prompt)

    if long_term_memories:
        if isinstance(long_term_memories, dict):
            # 按分类组织的记忆
            memory_sections = []
            category_names = {
                "喜好": "他的喜好",
                "习惯": "他的习惯",
                "事件": "他的经历和计划",
                "承诺": "他对你的承诺",
                "其他": "关于他的其他事情",
            }
            for cat in ["喜好", "习惯", "事件", "承诺", "其他"]:
                if cat in long_term_memories and long_term_memories[cat]:
                    items = long_term_memories[cat]
                    memory_sections.append(f"### {category_names.get(cat, cat)}")
                    memory_sections.extend(f"- {m}" for m in items)
            if memory_sections:
                parts.append(f"\n## 你记住的关于他的事情\n" + "\n".join(memory_sections))
        else:
            # 兼容旧的平铺列表格式
            memory_text = "\n".join(f"- {m}" for m in long_term_memories)
            parts.append(f"\n## 你记住的关于他的事情\n{memory_text}")
        # 添加自然引用记忆的指令
        parts.append("\n小贴士：偶尔在回复中自然提起你记住的事情，会让他感觉被在乎。比如「上次你说喜欢吃火锅，今天去吃了吗？」，但不要每条消息都提，自然就好。")

    return "\n".join(parts)
