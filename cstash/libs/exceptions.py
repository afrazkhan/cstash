import logging

logging.getLogger().setLevel('ERROR')

class CstashGeneralError(Exception):
    pass

class CstashUpdateError(Exception):
    pass

class CstashLoggingError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        logging.error(message)

class CstashCriticalException(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        logging.error(message)

        exit(1)
