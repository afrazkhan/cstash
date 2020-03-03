# https://pythonhosted.org/python-gnupg/#decryption
# https://stackoverflow.com/questions/50532695/embed-filename-using-python-gnupg

import logging

class GPG():
    def __init__(self, log_level):
        logging.getLogger().setLevel(log_level)

    def encrypt(self, filename):
        logging.debug(filename)
