import json
import socket
import textwrap
import uuid
from adapters.base import DCCAdapter
from typing import Any

from core.exceptions import DCCConnectionError, DCCExecutionError


class MayaAdapter(DCCAdapter):
    def __init__(self,host:str,port:int,timeout:int):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
    def connect(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect((self.host,self.port))
        except OSError as e:
            raise DCCConnectionError("Mayaとの接続に失敗しました。")
    def execute(self,code:str)->dict[str,Any]:
        self.execute_id = "maya_id_" + uuid.uuid4().hex
        wrapped = self._wrap_code_store(code)
        fetch_code = self._wrap_code_fetch()
        wrapped = self._to_mel(wrapped)
        fetch_code = self._to_mel(fetch_code)
        print("wrapped length:", len(wrapped))
        print("fetch_code length:", len(fetch_code))
        self.sock.sendall((wrapped+"\n").encode())#改行を含まないとTimeOut
        chunks=[]
        while True:
            chunk = self.sock.recv(4096)
            print(repr(chunk))
            chunks.append(chunk)
            if b"\n" in chunk:
                break
        self.connect()
        self.sock.sendall(fetch_code.encode())#改行を含むとTimeOut
        chunks=[]
        while True:
            chunk = self.sock.recv(4096)
            print(repr(chunk))
            chunks.append(chunk)
            if b"\n" in chunk:
                break
        response = b''.join(chunks).decode()
        response = response.strip("\n\x00")
        try:
            response = json.loads(response)
        except json.decoder.JSONDecodeError as e:
            raise DCCExecutionError("JSONDecodeError")
        if "status" not in response:
            raise DCCExecutionError("Mayaからの応答が不正です")
        result = response
        if result.get("status") == "error":
            raise DCCExecutionError(result.get("message", ""))
        return result
    def get_scene_info(self):
        pass
    def get_logs(self,lines:int=100)->list[str]:
        pass
    def _wrap_code_store(self,code:str)->str:
        indented = textwrap.indent(code,"    ")

        return (
            "import json\n"
            "try:\n"
            f"{indented}\n"
            f"    {self.execute_id} = (json.dumps({{\"status\":\"ok\"}}))\n"
            f"    print({self.execute_id})\n"
            "except Exception as e:\n"  
            f"    {self.execute_id} = (json.dumps({{\"status\":\"error\",\"message\":str(e)}}))\n"
            f"    print({self.execute_id})\n"
        )
    def _wrap_code_fetch(self)->str:
        return self.execute_id

    def _to_mel(self,python_code:str)->str:
        mel = python_code.replace('"','\\"')
        mel = mel.replace('\n','\\n')
        return f'python("{mel}")'
    def get_dcc_type(self) -> str:
        return "maya"