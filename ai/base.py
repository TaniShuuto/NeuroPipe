from abc import ABC, abstractmethod
class AIBackend(ABC):
    @abstractmethod
    def analyze(self,text:str,context:str) -> str:
        pass
    @abstractmethod
    def generate_code(self, language:str,dcc:str,prompt:str) -> str:
        pass
    @abstractmethod
    def is_available(self) -> bool:
        pass

