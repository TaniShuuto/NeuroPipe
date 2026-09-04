import json
import socket
import textwrap

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
        wrapped = self._wrap_code(code)
        self.sock.sendall(wrapped.encode())
        chunks=[]
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        response = b''.join(chunks).decode()
        result = json.loads(response)
        if result.get("status") == "error":
            raise DCCExecutionError(result.get("message", ""))
        return result
    def get_scene_info(self):
        pass
    def get_logs(self,lines:int=100)->list[str]:
        pass
    def _wrap_code(self,code:str)->str:
        indented = textwrap.indent(code,"    ")
        return (
            "import json\n"
            "try:\n"
            f"{indented}\n"
            "    print(json.dumps({\"status\":\"ok\"}))\n"
            "except Exception as e:\n"
            "    print(json.dumps({\"status\":\"error\",\"message\":str(e)}))\n"
        )