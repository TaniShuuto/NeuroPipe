from typing import Any
from abc import ABC, abstractmethod
class DCCAdapter(ABC):
    @abstractmethod
    def connect(self):
        pass
    @abstractmethod
    def execute(self, code:str) -> dict[str,Any]:
        pass
    @abstractmethod
    def get_scene_info(self):
        pass
    @abstractmethod
    def get_logs(self,lines:int=100)->list[str]:
        pass

