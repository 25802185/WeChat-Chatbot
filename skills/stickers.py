import random
import logging
from skills.base import Skill

log = logging.getLogger(__name__)


class StickerSkill(Skill):
    name = "表情包"
    description = "随机发送可爱的表情文字"

    def __init__(self, llm):
        self.llm = llm
        self._stickers = [
            "(っ˘ω˘ς) 摸摸头~",
            "(≧▽≦) 开心！",
            "(´• ω •`) ノ 嗨嗨~",
            "(￣▽￣)ノ 挥手手~",
            "(*/ω＼*) 害羞...",
            "(｡>﹏<｡) 委屈巴巴",
            "( •̀ ω •́ )✧ 加油！",
            "(╥﹏╥) 呜呜呜...",
            "(ノ◕ヮ◕)ノ*:・゚✧ 闪闪发光~",
            "٩(◕‿◕｡)۶ 抱抱！",
            "(¬‿¬) 嘿嘿~",
            "(；´д｀) 好累啊...",
            "(*≧∀≦*) 超开心！",
            "(｡･ω･｡) 萌萌哒~",
            "(ノ°▽°)ノ ヾ(≧▽≦*)o",
            "♥(´∀`) 爱你~",
            "(；´д`) 哼！",
            "(｡>﹏<｡) 不开心...",
            "(◕ᴗ◕✿) 乖巧~",
            "₍ᐢ..ᐢ₎ 可爱~",
        ]

    def check_trigger(self, context: dict) -> bool:
        if context.get("type") == "command":
            text = context.get("text", "")
            return any(kw in text for kw in ["表情", "表情包", "发个表情", "可爱"])
        return False

    def execute(self, context: dict) -> str | None:
        return random.choice(self._stickers)
