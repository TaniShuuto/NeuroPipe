from adapters.base import DCCAdapter
from ai.base import AIBackend
from core.exceptions import DCCExecutionError, ToolExecutionError


def loop(prompt:str, dcc:DCCAdapter, ai:AIBackend, language:str, loopcount:int) -> dict:
    if loopcount <= 0:
        raise ToolExecutionError("ループ回数は0以上である必要があります")
    context = ""
    status = ""
    dcc_type = dcc.get_dcc_type()
    for i in range(loopcount):
        code = ai.generate_code(language, dcc_type, prompt + context,)
        dcc.connect()
        try:
            dcc.execute(code)
            status = "ok"
            break
        except DCCExecutionError as e:
            context = prompt + code + str(e)
            status = "error"
            continue

    return {"status":status,"code":f"{code}"}

