from abc import ABC, abstractmethod
class AIBackend(ABC):
    @abstractmethod
    def analyze(self,text:str,context:str) -> str:
        pass
    @abstractmethod
    def generate_code(self, prompt:str,language:str) -> str:
        pass
    @abstractmethod
    def is_available(self) -> bool:
        pass

