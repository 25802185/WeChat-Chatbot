from openai import OpenAI

class LLM:
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-v4-pro",
                 max_tokens: int = 1024, temperature: float = 0.85):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, system_prompt: str, history: list[dict]) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content
