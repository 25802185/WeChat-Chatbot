import logging
from openai import OpenAI

log = logging.getLogger(__name__)

class LLM:
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-v4-pro",
                 max_tokens: int = 1024, temperature: float = 0.85):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, system_prompt: str, history: list[dict]) -> str | None:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content
            return content if content else None
        except Exception as e:
            log.error(f"LLM API 调用失败: {e}")
            return None
