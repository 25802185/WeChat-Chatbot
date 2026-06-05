import signal
import sys
import logging
from wcferry import Wcf, WxMsg
from config import load_config
from bot import Bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def main():
    cfg = load_config()
    bot = Bot(cfg)

    wcf = Wcf()
    log.info(f"已登录，wxid: {wcf.get_self_wxid()}")
    log.info(f"虚拟恋人 [{cfg['character']['name']}] 启动成功，等待消息...")

    wcf.enable_receiving_msg()

    def shutdown(sig, frame):
        log.info("正在关闭...")
        wcf.disable_recv_msg()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    while True:
        msg: WxMsg = wcf.get_msg()
        reply = bot.handle_message(msg.sender, msg.content, msg.type)
        if reply:
            wcf.send_text(reply, msg.sender)
            log.info(f"回复 {msg.sender}: {reply[:50]}...")


if __name__ == "__main__":
    main()
