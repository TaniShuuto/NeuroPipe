from ai.base import AIBackend
import requests
class OllamaBackend(AIBackend):
    def __init__(self,host:str,model:str):
        self.host = host
        self.model = model

    def analyze(self,text:str,context:str) -> str:
        pass
    def generate_code(self, prompt:str,language:str) -> str:
        pass
    def is_available(self) -> bool:
        try:
            available = requests.get(self.host)
            return available.status_code == 200
        except Exception:
            return False
