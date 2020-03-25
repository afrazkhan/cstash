import cstash.libs.helpers as helpers
import logging
import gnupg
import os
import cstash.libs.exceptions as exceptions

class GPG():
    def __init__(self, cstash_directory, log_level=None):
        helpers.set_logger(level=log_level)
        self.cstash_directory = cstash_directory
        self.gpg = gnupg.GPG(gnupghome="{}/.gnupg".format(os.path.expanduser('~')))

    def encrypt(self, source_filepath, key, destination_filepath):
        """
        Encrypt [source_filepath] to [destination_filepath].

        Return [encrypted_filepath] for success or False for failure.
        """

        try:
            stream = open(source_filepath, "rb")
            self.gpg.encrypt_file(stream, key, armor=False, output=destination_filepath)
        except Exception as e:
            logging.error("Couldn't encrypt {}: {}".format(source_filepath, e))
            return False

        return destination_filepath

    def decrypt(self, filepath, destination):
        """
        Decrypt [filepath] to [destination]
        """

        stream = open(filepath, "rb")
        helpers.recreate_directories(destination, helpers.strip_path(filepath)[0])
        encrypted_filepath = destination or "{self.location}/{}".format()
        self.gpg.decrypt_file(stream, output=encrypted_filepath)

        return encrypted_filepath
