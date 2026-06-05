import signal
import sys
import time
import logging
from config import load_config
from bot import Bot
from weixin_api import WeixinApi, extract_text
from skills import create_default_skills

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def main():
    cfg = load_config()
    bot = Bot(cfg)
    api = WeixinApi(data_dir=cfg.get("weixin", {}).get("data_dir", "data"))

    if not api.load_login():
        log.info("未找到登录凭证，开始扫码登录...")
        if not api.login(cfg.get("weixin", {}).get("bot_type", "3")):
            log.error("登录失败，退出")
            sys.exit(1)

    skills = create_default_skills(bot.llm, bot.memory, cfg)
    name = cfg["character"]["name"]
    print(f"\n虚拟恋人 [{name}] 启动成功，等待消息...\n")

    running = True
    last_user_id = ""
    last_context_token = ""
    last_skill_check = 0

    def shutdown(sig, frame):
        nonlocal running
        log.info("正在关闭...")
        running = False

    signal.signal(signal.SIGINT, shutdown)

    buf = ""
    while running:
        resp = api.get_updates(buf)
        if resp.get("ret", 0) != 0:
            log.warning(f"getUpdates 返回错误: ret={resp.get('ret')} err={resp.get('errmsg')}")
            time.sleep(5)
            continue

        buf = resp.get("get_updates_buf", "")
        for msg in resp.get("msgs", []):
            if msg.get("message_type") != 1:
                continue

            text = extract_text(msg)
            if not text:
                continue

            sender = msg.get("from_user_id", "")
            context_token = msg.get("context_token", "")

            last_user_id = sender
            last_context_token = context_token

            log.info(f"收到消息 [{sender}]: {text[:50]}...")

            skill_reply = skills.check_command(text)
            if skill_reply:
                api.send_message(sender, skill_reply, context_token)
                log.info(f"技能回复 [{sender}]: {skill_reply[:50]}...")
                continue

            reply = bot.handle_text_message(sender, text)
            if reply:
                if api.send_message(sender, reply, context_token):
                    log.info(f"已回复 [{sender}]: {reply[:50]}...")
                else:
                    log.error(f"回复失败 [{sender}]")

        now = time.time()
        if last_user_id and now - last_skill_check >= 60:
            last_skill_check = now
            skill_context = {
                "type": "timer",
                "last_user_id": last_user_id,
                "last_context_token": last_context_token,
            }
            skill_msgs = skills.check_and_execute(skill_context)
            for msg_text in skill_msgs:
                if api.send_message(last_user_id, msg_text, last_context_token):
                    log.info(f"技能主动消息: {msg_text[:50]}...")

        time.sleep(1)


if __name__ == "__main__":
    main()
