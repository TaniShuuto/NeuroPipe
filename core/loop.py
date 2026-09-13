from adapters.base import DCCAdapter
from ai.base import AIBackend
from core.config import load_config
from adapters.maya import MayaAdapter
from core.exceptions import DCCExecutionError

def loop(prompt:str,dcc:DCCAdapter,ai:AIBackend,language:str,loopcount:int) -> dict:
    context = ""
    status = ""
    for i in range(loopcount):
        code = ai.generate_code(prompt + context,language)
        dcc.connect()
        try:
            dcc.execute(code)
            status = "ok"
            break
        except DCCExecutionError as e: #as e が必要か分からないです。
            context = prompt + code + str(e)
            status = "error"
            continue

    return {"status":status,"code":f"{code}"}