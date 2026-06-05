EMOTION_KEYWORDS = {
    "开心": ["哈哈哈", "嘻嘻", "开心", "高兴", "太好了", "耶", "嘿嘿", "棒", "厉害", "笑死", "快乐", "haha", "lol", "666", "好棒", "爽"],
    "难过": ["难过", "伤心", "哭了", "委屈", "呜呜", "不开心", "郁闷", "心疼", "惨了", "难受", "失落", "寂寞", "心碎", "泪"],
    "生气": ["生气", "气死", "讨厌", "烦死", "可恶", "受不了", "滚蛋", "愤怒", "恼火", "气人"],
    "疲惫": ["累死", "困死", "好累", "好困", "想睡", "加班", "熬夜", "没精神", "疲惫", "撑不住", "腰酸"],
    "撒娇": ["抱抱", "亲亲", "想你", "爱你", "宝贝", "人家", "求你", "哄我", "陪我", "粘你", "要亲亲"],
    "焦虑": ["担心", "害怕", "紧张", "焦虑", "不安", "怎么办", "完了", "出事", "慌了", "崩溃"],
    "无聊": ["无聊", "好闲", "没事干", "好无聊", "闲得", "发呆", "没意思"],
}

NEGATION_WORDS = ["不", "没", "别", "无", "未", "非"]


def detect_emotion(text: str) -> str:
    scores: dict[str, int] = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = 0
        for kw in keywords:
            idx = text.find(kw)
            while idx != -1:
                if idx > 0 and text[idx - 1] in NEGATION_WORDS:
                    pass
                else:
                    count += 1
                idx = text.find(kw, idx + len(kw))
        if count > 0:
            scores[emotion] = count

    if not scores:
        return "neutral"

    return max(scores, key=scores.get)


import re
import random

# Emoji检测正则
EMOJI_PATTERN = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags
    u"\U00002702-\U000027B0"  # dingbats
    u"\U000024C2"             # enclosed M
    u"\U0001F170-\U0001F251"  # enclosed alphanumerics & ideographic supplement
    "]+", flags=re.UNICODE)

# 情绪-emoji映射表
EMOTION_EMOJI_MAP = {
    "开心": ["😊", "😄", "💖", "✨"],
    "撒娇": ["💕", "🥺", "😘", "🥰"],
    "害羞": ["🙈", "😳", "💕", "😊"],
    "难过": ["🥺", "😢", "💔"],
    "生气": ["😤", "💢"],
    "疲惫": ["😪", "💤"],
    "焦虑": ["😰", "😟"],
    "想念": ["💭", "💕", "🥺", "😘"],
}


def has_emoji(text: str) -> bool:
    """检测文本是否包含emoji"""
    return bool(EMOJI_PATTERN.search(text))


def get_emoji_for_emotion(emotion: str) -> str | None:
    """根据情绪返回随机emoji，无匹配返回None"""
    emojis = EMOTION_EMOJI_MAP.get(emotion)
    if emojis:
        return random.choice(emojis)
    return None
