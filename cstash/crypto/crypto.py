"""
Calls the appropriate module to perform encryption tasks. At the moment
only GnuPG is supported.
"""

import logging
import cstash.libs.helpers as helpers
import cstash.libs.exceptions as cstash_exceptions

class Encryption():
    def __init__(self, cstash_directory, cryptographer, log_level):
        if cryptographer == 'gpg':
            logging.getLogger().setLevel(log_level)
            self.log_level = log_level

            from cstash.crypto.gpg import GPG
            self.encryptor = GPG(cstash_directory, log_level)

        self.cstash_directory = cstash_directory

    def encrypt(self, source_filepath, destination_filename, key, cstash_directory=None):
        """
        Encrypt [source_filepath] into the [cstash_directory] as [destination_filename] using [key].

        Return the complete path for the encrypted file for success, or raise a
        CstashCriticalException
        """

        encrypted_filepath = f"{self.cstash_directory}/{destination_filename}"

        encrypted_filename = self.encryptor.encrypt(
            source_filepath=source_filepath, key=key, destination_filepath=encrypted_filepath)
        if encrypted_filename != False:
            return encrypted_filename
        else:
            raise cstash_exceptions.CstashCriticalException(message=encrypted_filename)

    def decrypt(self, filepath, destination):
        """
        Decrypt [filepath] to [destination]

        Return the complete path for the decrypted file for success, or raise a
        CstashCriticalException
        """

        decrypted_filename = self.encryptor.decrypt(filepath, helpers.clear_path(destination))
        if decrypted_filename != False:
            return decrypted_filename
        else:
            raise cstash_exceptions.CstashCriticalException(message=decrypted_filename)
