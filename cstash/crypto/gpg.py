import cstash.libs.helpers as helpers
import logging
import gnupg
import os

class GPG():
    def __init__(self, cstash_directory, key, log_level=None):
        helpers.set_logger(level=log_level)
        self.cstash_directory = cstash_directory
        self.key = key
        self.gpg = gnupg.GPG(gnupghome="{}/.gnupg".format(os.path.expanduser('~')))

    def encrypt(self, filepath, obsfucated_name):
        """
        TODO: Encrypt [filepath] to temporary storage in the Cstash directory, and return
        the path to the encrypted object, or False for failure
        """

        stream = open(filepath, "rb")
        import pdb; pdb.set_trace()
        helpers.recreate_directories(self.cstash_directory, filepath)
        encrypted_filepath = "{}/{}".format(self.cstash_directory, obsfucated_name)
        self.gpg.encrypt_file(stream, self.key, armor=False, output=encrypted_filepath)

        return encrypted_filepath
