from fastapi import FastAPI
from pydantic import BaseModel
from ai.ollama import OllamaBackend
from core.config import load_config
class AnalyzeRequest(BaseModel):
    text: str
    context:str = ""


app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    config = load_config()
    ollama = OllamaBackend(
        host=config["ai"]["ollama"]["host"],
        model=config["ai"]["ollama"]["model_analyze"],
    )
    return ollama.analyze(request.text, request.context)

