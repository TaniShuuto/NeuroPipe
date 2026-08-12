
class DCCAdapterError(Exception):
    pass
class DCCConnectionError(DCCAdapterError):
    pass
class DCCExecutionError(DCCAdapterError):
    pass
