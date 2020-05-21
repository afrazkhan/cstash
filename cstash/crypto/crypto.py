"""
Calls the appropriate module to perform encryption tasks. At the moment
only GnuPG is supported.
"""

import cstash.libs.helpers as helpers
import cstash.libs.exceptions as cstash_exceptions

class Encryption():
    """
    Abstraction class that passes requests down to chosen [cryptographer]
    """

    def __init__(self, cstash_directory, cryptographer, log_level="ERROR", extra_args={}):
        self.cstash_directory = cstash_directory

        if cryptographer == 'gpg':
            from cstash.crypto.gpg import GPG
            self.encryptor = GPG(cstash_directory=cstash_directory,
                                 log_level=log_level,
                                 gnupg_home=extra_args.get("gnupg_home"))

        if cryptographer == 'python':
            from cstash.crypto.pcrypt import PCrypt
            self.encryptor = PCrypt(cstash_directory=cstash_directory,
                                    log_level=log_level)

    def encrypt(self, source_filepath, destination_filename, key):
        """
        Encrypt [source_filepath] into the [cstash_directory] as [destination_filename] using [key].

        Return the complete path for the encrypted file for success, or raise a
        CstashCriticalException
        """

        encrypted_filepath = f"{self.cstash_directory}/{destination_filename}"

        encrypted_filename = self.encryptor.encrypt(
            source_filepath=source_filepath, key=key, destination_filepath=encrypted_filepath)
        if encrypted_filename is not False:
            return encrypted_filename

        raise cstash_exceptions.CstashCriticalException(message=encrypted_filename)

    def decrypt(self, filepath, destination, key, password=None):
        """
        Decrypt [filepath] to [destination]

        Return the complete path for the decrypted file for success, or raise a
        CstashCriticalException
        """

        decrypted_filename = self.encryptor.decrypt(filepath, helpers.clear_path(destination), key, password)
        if decrypted_filename is not False:
            return decrypted_filename

        raise cstash_exceptions.CstashCriticalException(message=decrypted_filename)
