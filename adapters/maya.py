import json
import socket

from adapters.base import DCCAdapter
from typing import Any

from core.exceptions import DCCConnectionError


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
        self.sock.sendall(code.encode())
        chunks=[]
        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        response = b''.join(chunks).decode()
        return {"response":response}
    def get_scene_info(self):
        pass
    def get_logs(self,lines:int=100)->list[str]:
        pass