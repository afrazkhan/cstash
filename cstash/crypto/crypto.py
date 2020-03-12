"""
Calls the appropriate module to do encryption. At the moment it only does GnuPG
"""

import logging
import cstash.libs.exceptions as cstash_exceptions

class Encryption():
    def __init__(self, cstash_directory, cryptographer, key, log_level):
        if cryptographer is 'gpg':
            logging.getLogger().setLevel(log_level)
            self.log_level = log_level

            from cstash.crypto.gpg import GPG
            self.encryptor = GPG(cstash_directory, key, log_level)

        self.cstash_directory = cstash_directory

    def encrypt(self, filepath, obsfucated_name, cstash_directory=None):
        """
        Encrypt [filepath] into the [cstash_directory].

        Return the complete path for the encrypted file for success, or raise a
        CstashCriticalException
        """

        encrypted_filename = self.encryptor.encrypt(filepath, obsfucated_name)
        if encrypted_filename != False:
            return encrypted_filename
        else:
            raise cstash_exceptions.CstashCriticalException()
