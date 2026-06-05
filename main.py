import signal
import sys
import logging
from config import load_config
from bot import Bot
from weixin_api import WeixinApi, extract_text

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

    name = cfg["character"]["name"]
    print(f"\n虚拟恋人 [{name}] 启动成功，等待消息...\n")

    running = True

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

            log.info(f"收到消息 [{sender}]: {text[:50]}...")

            reply = bot.handle_text_message(sender, text)
            if reply:
                if api.send_message(sender, reply, context_token):
                    log.info(f"已回复 [{sender}]: {reply[:50]}...")
                else:
                    log.error(f"回复失败 [{sender}]")


if __name__ == "__main__":
    main()
