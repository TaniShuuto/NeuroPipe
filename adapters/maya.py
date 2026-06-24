from adapters.base import DCCAdapter
from typing import Any
class MayaAdapter(DCCAdapter):
    def connect(self):
        pass
    def execute(self,code:str)->dict[str,Any]:
        pass
    def get_scene_info(self):
        pass
    def get_logs(self,lines:int=100)->list[str]:
        pass