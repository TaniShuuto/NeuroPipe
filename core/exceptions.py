
class DCCAdapterError(Exception):
    pass
class DCCConnectionError(DCCAdapterError):
    pass
class DCCExecutionError(DCCAdapterError):
    pass
class DCCSyntaxError(DCCExecutionError):
    pass
class AIError(Exception):
    pass
class AIConnectionError(AIError):
    pass
class AIGenerateError(AIError):
    pass
class ToolError(Exception):
    pass
class ToolConnectionError(ToolError):
    pass
class ToolExecutionError(ToolError):
    pass