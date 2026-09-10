from fastapi import FastAPI
from pydantic import BaseModel
from ai.ollama import OllamaBackend
from core.config import load_config
from adapters.maya import MayaAdapter
class AnalyzeRequest(BaseModel):
    text: str
    context:str = ""
class ExecuteRequest(BaseModel):
    code:str


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

@app.post("/execute")
def execute(request: ExecuteRequest):
    config = load_config()
    maya =MayaAdapter(
        host=config["dcc"]["maya"]["host"],
        port=config["dcc"]["maya"]["port"],
        timeout=config["dcc"]["maya"]["timeout"]
    )
    maya.connect()
    return maya.execute(request.code)