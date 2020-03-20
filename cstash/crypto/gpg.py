import cstash.libs.helpers as helpers
import logging
import gnupg
import os
import cstash.libs.exceptions as exceptions

class GPG():
    def __init__(self, cstash_directory, key, log_level=None):
        helpers.set_logger(level=log_level)
        self.cstash_directory = cstash_directory
        self.key = key
        self.gpg = gnupg.GPG(gnupghome="{}/.gnupg".format(os.path.expanduser('~')))

    def encrypt(self, filepath, obsfucated_name=None, destination=None):
        """
        Encrypt [filepath] to temporary storage in the Cstash directory, and return
        the path to the encrypted object, or False for failure. Alternatively, override
        the usual output destination and filename with [destination].

        One of either [obsfucated_name] or [destination] are required
        """

        if not obsfucated_name and not destination:
            raise exceptions.CstashCriticalException(message="One of either obsfucated_name or destination are needed")

        stream = open(filepath, "rb")
        helpers.recreate_directories(self.cstash_directory, filepath)
        encrypted_filepath = destination or f"{self.cstash_directory}/{obsfucated_name}"
        self.gpg.encrypt_file(stream, self.key, armor=False, output=encrypted_filepath)

        return encrypted_filepath
