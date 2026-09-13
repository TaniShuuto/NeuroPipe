
class DCCAdapterError(Exception):
    pass
class DCCConnectionError(DCCAdapterError):
    pass
class DCCExecutionError(DCCAdapterError):
    pass
class AIError(Exception):
    pass
class AIConnectionError(AIError):
    pass
class AIGenerateError(AIError):
    pass