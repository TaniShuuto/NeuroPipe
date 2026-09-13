from abc import ABC, abstractmethod
from typing import Any


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
    @abstractmethod
    def get_dcc_type(self) -> str:
        pass
