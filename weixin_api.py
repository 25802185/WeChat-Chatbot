import json
import os
import random
import logging
import requests
import qrcode as qrcode_lib

log = logging.getLogger(__name__)

FIXED_BASE_URL = "https://ilinkai.weixin.qq.com"
DEFAULT_BOT_TYPE = "3"
LONG_POLL_TIMEOUT_S = 35


def _random_wechat_uin() -> str:
    uint32 = random.randint(0, 2**32 - 1)
    return __import__("base64").b64encode(str(uint32).encode()).decode()


class WeixinApi:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.login_file = os.path.join(data_dir, "login.json")
        self.token: str | None = None
        self.base_url: str | None = None
        self.bot_id: str | None = None
        os.makedirs(data_dir, exist_ok=True)

    def load_login(self) -> bool:
        if not os.path.exists(self.login_file):
            return False
        try:
            with open(self.login_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.token = data.get("token")
            self.base_url = data.get("base_url")
            self.bot_id = data.get("bot_id")
            if self.token and self.base_url:
                log.info(f"已加载登录凭证: bot_id={self.bot_id}")
                return True
        except Exception as e:
            log.warning(f"加载登录凭证失败: {e}")
        return False

    def _save_login(self):
        data = {
            "token": self.token,
            "base_url": self.base_url,
            "bot_id": self.bot_id,
        }
        with open(self.login_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _build_headers(self, with_token: bool = True) -> dict:
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "X-WECHAT-UIN": _random_wechat_uin(),
            "iLink-App-Id": "bot",
            "iLink-App-ClientVersion": "131584",
        }
        if with_token and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _post(self, base_url: str, endpoint: str, body: dict, timeout: int = 15) -> dict:
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        resp = requests.post(url, json=body, headers=self._build_headers(with_token=True), timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _get(self, base_url: str, endpoint: str, timeout: int = 40) -> dict:
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        resp = requests.get(url, headers=self._build_headers(with_token=False), timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def login(self, bot_type: str = DEFAULT_BOT_TYPE) -> bool:
        log.info("正在获取登录二维码...")

        local_token_list = []
        if self.token:
            local_token_list.append(self.token)

        qr_resp = self._post(
            FIXED_BASE_URL,
            f"ilink/bot/get_bot_qrcode?bot_type={bot_type}",
            {"local_token_list": local_token_list},
        )

        qrcode_url = qr_resp.get("qrcode_img_content") or qr_resp.get("qrcode")
        if not qrcode_url:
            log.error(f"获取二维码失败: {qr_resp}")
            return False

        qr = qrcode_lib.QRCode(box_size=1, border=1)
        qr.add_data(qrcode_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
        print(f"\n若二维码无法扫描，请访问: {qrcode_url}\n")

        qrcode_token = qr_resp.get("qrcode")
        if not qrcode_token:
            log.error("响应中缺少 qrcode token")
            return False

        log.info("请用微信扫描二维码...")
        return self._poll_qr_status(qrcode_token)

    def _poll_qr_status(self, qrcode: str) -> bool:
        current_base = FIXED_BASE_URL
        scaned_printed = False

        for _ in range(300):
            try:
                resp = self._get(
                    current_base,
                    f"ilink/bot/get_qrcode_status?qrcode={qrcode}",
                    timeout=40,
                )
            except requests.Timeout:
                continue
            except Exception as e:
                log.warning(f"轮询二维码状态异常: {e}")
                continue

            status = resp.get("status")

            if status == "wait":
                pass
            elif status == "scaned":
                if not scaned_printed:
                    print("已扫码，等待确认...")
                    scaned_printed = True
            elif status == "confirmed":
                self.token = resp.get("bot_token")
                self.base_url = resp.get("baseurl")
                self.bot_id = resp.get("ilink_bot_id")

                if not self.token or not self.base_url:
                    log.error("登录确认但缺少 token 或 baseurl")
                    return False

                self._save_login()
                log.info(f"登录成功! bot_id={self.bot_id}")
                print("登录成功!")
                return True
            elif status == "expired":
                log.warning("二维码已过期")
                print("二维码已过期，请重新运行程序")
                return False
            elif status == "scaned_but_redirect":
                redirect_host = resp.get("redirect_host")
                if redirect_host:
                    current_base = f"https://{redirect_host}"
                    log.info(f"IDC 重定向到: {current_base}")
            elif status == "binded_redirect":
                log.info("已连接过，无需重复连接")
                if self.load_login():
                    return True
                return False

            import time
            time.sleep(1)

        log.warning("登录超时")
        return False

    def get_updates(self, buf: str = "") -> dict:
        body = {
            "get_updates_buf": buf,
            "base_info": {"channel_version": "2.4.4", "bot_agent": "VirtualLover/1.0"},
        }
        try:
            return self._post(self.base_url, "ilink/bot/getupdates", body, timeout=40)
        except requests.Timeout:
            return {"ret": 0, "msgs": [], "get_updates_buf": buf}
        except Exception as e:
            log.error(f"getUpdates 失败: {e}")
            return {"ret": -1, "msgs": [], "get_updates_buf": buf}

    def send_message(self, to_user_id: str, text: str, context_token: str = "") -> bool:
        body = {
            "msg": {
                "to_user_id": to_user_id,
                "context_token": context_token,
                "message_type": 2,
                "message_state": 2,
                "item_list": [
                    {"type": 1, "text_item": {"text": text}}
                ],
            },
            "base_info": {"channel_version": "2.4.4", "bot_agent": "VirtualLover/1.0"},
        }
        try:
            self._post(self.base_url, "ilink/bot/sendmessage", body)
            return True
        except Exception as e:
            log.error(f"发送消息失败: {e}")
            return False


def extract_text(msg: dict) -> str:
    for item in msg.get("item_list", []):
        if item.get("type") == 1:
            text = item.get("text_item", {}).get("text")
            if text:
                return str(text)
        elif item.get("type") == 3:
            voice_text = item.get("voice_item", {}).get("text")
            if voice_text:
                return str(voice_text)
    return ""
