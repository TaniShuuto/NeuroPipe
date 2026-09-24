from fastapi import FastAPI,HTTPException
from fastapi.exceptions import FastAPIError
from pydantic import BaseModel
from ai.ollama import OllamaBackend
from core.config import load_config
from adapters.maya import MayaAdapter
from core.exceptions import DCCConnectionError, AIGenerateError, AIConnectionError, DCCExecutionError
from core.loop import loop
class AnalyzeRequest(BaseModel):
    text: str
    context:str = ""
    include_scene_info:bool = False
class ExecuteRequest(BaseModel):
    code:str
class LoopRequest(BaseModel):
    prompt: str
    loop_count: int
    language: str


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

    try:
        if request.include_scene_info:
            maya =MayaAdapter(
                host=config["dcc"]["maya"]["host"],
                port=config["dcc"]["maya"]["port"],
                timeout=config["dcc"]["maya"]["timeout"]
            )
            maya.connect()
            scene_info = maya.get_scene_info()
        else:
            scene_info = ""
        result = ollama.analyze(request.text,request.context,scene_info)
    except AIGenerateError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except AIConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DCCExecutionError as e:
        raise HTTPException(status_code=502, detail= str(e))
    except DCCConnectionError as e:
        raise HTTPException(status_code=503, detail= str(e))
    return result

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

@app.post("/loop")
def run_loop(request: LoopRequest):
    config = load_config()
    maya =MayaAdapter(
        host=config["dcc"]["maya"]["host"],
        port=config["dcc"]["maya"]["port"],
        timeout=config["dcc"]["maya"]["timeout"]
    )
    ollama = OllamaBackend(
        host=config["ai"]["ollama"]["host"],
        model=config["ai"]["ollama"]["model_analyze"],
    )
    try:
        loop_status = loop(request.prompt, maya, ollama, request.language, request.loop_count)
    except AIGenerateError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except DCCConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except AIConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return loop_status