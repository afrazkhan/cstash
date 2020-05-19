"""
Exceptions for Cstash
"""

import logging

class CstashGeneralError(Exception):
    pass

class CstashUpdateError(Exception):
    pass

class CstashUploadError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        logging.error(message)

class CstashCriticalException(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        logging.error(message)

        import sys

        sys.exit(1)
