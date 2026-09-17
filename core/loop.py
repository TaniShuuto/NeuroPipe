from adapters.base import DCCAdapter
from ai.base import AIBackend
from core.exceptions import DCCConnectionError, DCCExecutionError, ToolExecutionError, AIGenerateError
from core.config import load_config

def loop(prompt:str, dcc:DCCAdapter, ai:AIBackend, language:str, loop_count:int) -> dict:
    if loop_count <= 0:
        raise ToolExecutionError("ループ回数は0以上である必要があります")
    config = load_config()
    try_counter = config["ai"]["trycount"]
    context = ""
    status = ""
    loop_number = 0
    n = 0
    dcc_type = dcc.get_dcc_type()
    for i in range(loop_count):
        for j in range(try_counter):
            try:
                code = ai.generate_code(language, dcc_type, prompt + context)
                break
            except AIGenerateError as e:
                n += 1
                print(f"生成失敗{n}")
                error_message = str(e)
                continue
        else:
            raise AIGenerateError(error_message)
        print(f"{code},\nループ回数{loop_number}\n")
        dcc.connect()
        try:
            dcc.execute(code)
            status = "ok"
            loop_number = loop_number + 1
            break
        except DCCExecutionError as e:
            context = prompt + code + str(e)
            status = "error"
            loop_number = loop_number + 1
            continue

    return {"status":status,"code":f"{code}","loop":loop_number}

