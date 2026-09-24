import json
import socket
import textwrap
import uuid
from adapters.base import DCCAdapter
from typing import Any

from core.exceptions import DCCConnectionError, DCCExecutionError,DCCSyntaxError


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
        try:
            compile(code,"<string>","exec")
        except SyntaxError as e:
            raise DCCSyntaxError(str(e))
        response = self.send_protocol(code)

        if "status" not in response:
            raise DCCExecutionError("Mayaからの応答が不正です")
        result = response
        if result.get("status") == "error":
            raise DCCExecutionError(result.get("message", ""))
        return result
    def get_scene_info(self):
        code = """
import maya.cmds as cmds
import maya.mel as mel
import os.path as path

def get_info(ename,is_primary):
    result = {}
    result["object_name"] = ename
    types = (cmds.listRelatives(ename, shapes=True))
    if types != None:
        c = types[0]
        result["type"] = (cmds.nodeType(c))
        if is_primary:
            conn = cmds.listConnections(c, s=False, d=True)
            mats = cmds.listConnections(conn, s=True, d=False)
            semats = cmds.ls(mats, mat=True)
            if not semats:
                result["material_name"] = None
            else:
                result["material_name"] = semats[0]
            result["vertex"] = (cmds.polyEvaluate(ename, v=1))
            result["edge"] = (cmds.polyEvaluate(ename, e=1))
            result["face"] = (cmds.polyEvaluate(ename, f=1))
            result["tri"] = (cmds.polyEvaluate(ename, t=1))
            result["uv"] = (cmds.polyEvaluate(ename, uv=1))
    else:
        result["type"] ="選択されているのはシェイプを持たないオブジェクトです"
        result["material_name"] = "マテリアルを持たないオブジェクトです"
    if is_primary:
        separnet = cmds.listRelatives(ename, parent=True)
        if not separnet:
            result["parent"] = None
        else:
            result["parent"] = separnet[0]
        result["visibility"] = (cmds.getAttr(ename + '.visibility'))
    result["rotate_x"] = cmds.getAttr(ename + '.rx')
    result["rotate_y"] = cmds.getAttr(ename + '.ry')
    result["rotate_z"] = cmds.getAttr(ename + '.rz')
    result["transform_x"] = cmds.getAttr(ename + '.tx')
    result["transform_y"] = cmds.getAttr(ename + '.ty')
    result["transform_z"] = cmds.getAttr(ename + '.tz')
    result["scale_x"] = cmds.getAttr(ename + '.sx')
    result["scale_y"] = cmds.getAttr(ename + '.sy')
    result["scale_z"] = cmds.getAttr(ename + '.sz')
    return result
count_max = 5
info = {
    "scene":{},
    "primary":{},
    "other":[

    ]
}
plists = []
scenePath = cmds.file(query=True, sceneName=True)
scene_name= path.basename(scenePath).replace(".mb", "")
if scene_name != "":
    info["scene"]["scene_name"] = scene_name
else:
    info["scene"]["scene_name"] = "シーン名が未保存か取得できません"
info["scene"]["object_all"]=len(cmds.ls(transforms=True))
me = cmds.ls(orderedSelection=True)
name = me[:count_max]
print(name)
info["scene"]["material_all"] = len(cmds.ls(mat = True))
if name != []:
    for i in range(len(name)):
        if i == 0:
            ename = name[i]
            info["primary"] = get_info(ename,i == 0)
        else:
            ename = name[i]
            info["other"].append(get_info(ename,i == 0))
else:
    info["primary"] ="選択なし"
    info["other"] = "選択なし"
        """
        response = self.send_protocol(code,"{\"status\":\"ok\",\"data\":str(info)}")
        return response

    def get_logs(self,lines:int=100)->list[str]:
        pass
    def _wrap_code_store(self,code:str,result:str = "{\"status\":\"ok\"}")->str:
        indented = textwrap.indent(code,"    ")

        return (
            "import json\n"
            "try:\n"
            f"{indented}\n"
            f"    {self.execute_id} = (json.dumps({result}))\n"
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
    def send_protocol(self,code,result:str = "{\"status\":\"ok\"}"):
        self.execute_id = "maya_id_" + uuid.uuid4().hex
        wrapped = self._wrap_code_store(code,result)
        fetch_code = self._wrap_code_fetch()
        wrapped = self._to_mel(wrapped)
        fetch_code = self._to_mel(fetch_code)
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
        return response