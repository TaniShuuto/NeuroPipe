import requests
import json

from requests import RequestException

from ai.base import AIBackend
from core.exceptions import AIConnectionError,AIGenerateError

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
        try:
            response = requests.post(url,json=payload)
        except RequestException as e:
            raise AIConnectionError(str(e))
        try:
            response = response.json()["response"]
        except json.decoder.JSONDecodeError:
            raise AIGenerateError("JSONDecodeError")
        except KeyError as e :
            raise AIGenerateError(f"Ollamaからの返答が不正です{str(e)}")
        return response
    def generate_code(self,language:str,dcc:str,prompt:str) -> str:
        prompt = (f"指定言語:{language}\n{dcc}で実行できるコードを生成してください."
                  f"以下の条件を達成してください.\n{prompt}")

        payload = {
            "model":self.model,
            "prompt":prompt,
            "stream":False,
            "format":{
                "type":"object",
                "properties":{
                    "code":{"type":"string"},
                },
                "required":["code"]
            }
        }
        url = self.host + "/api/generate"
        try:
            response = requests.post(url,json=payload)
        except RequestException as e:
            raise AIConnectionError(str(e))
        try:
            response = response.json()["response"]
        except json.decoder.JSONDecodeError:
            raise AIGenerateError("Ollamaからの応答が不正です.")
        except KeyError as e :
            raise AIGenerateError(f"Ollamaからの応答が不正です.{str(e)}")
        try:
            response = json.loads(response)
        except json.decoder.JSONDecodeError as e:
            raise AIGenerateError("JSONDecodeError")
        try:
            code = response["code"]
            return code
        except  KeyError as e :
            raise AIGenerateError(f"Ollamaからの返答が不正です{str(e)}")
    def is_available(self) -> bool:
        try:
            available = requests.get(self.host)
            return available.status_code == 200
        except Exception :
            return False