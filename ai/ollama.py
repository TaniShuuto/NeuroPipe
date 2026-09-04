import requests

from ai.base import AIBackend


class OllamaBackend(AIBackend):
    def __init__(self,host:str,model:str):
        self.host = host
        self.model = model

    def analyze(self,text:str,context:str) -> str:
        prompt = (f"以下のエラーを分析して解決策を提案してください."
                  f"補足情報がある場合、そちらの指示を優先してください.\n{text}")
        if context:
            prompt += f"\n補足情報:{context}"
        url = self.host + "/api/generate"
        payload = {
            "model":self.model,
            "prompt":prompt,
            "stream":False
        }
        response = requests.post(url,json=payload)
        return response.json()["response"]
    def generate_code(self, prompt:str,language:str) -> str:
        pass
    def is_available(self) -> bool:
        try:
            available = requests.get(self.host)
            return available.status_code == 200
        except Exception:
            return False
