# https://pythonhosted.org/python-gnupg/#decryption
# https://stackoverflow.com/questions/50532695/embed-filename-using-python-gnupg

import cstash.libs.helpers as helpers
import logging
import gnupg
import os

class GPG():
    def __init__(self, cstash_directory, key, log_level):
        logging.getLogger().setLevel(log_level)
        self.cstash_directory = cstash_directory
        self.key = key
        self.gpg = gnupg.GPG(gnupghome="{}/.gnupg".format(os.path.expanduser('~')))

    def encrypt(self, filename):
        """
        TODO: Encrypt [filename] to temporary storage in the Cstash directory, and return
        the path to the encrypted object, or False for failure
        """

        stream = open(filename, "rb")
        helpers.recreate_directories(self.cstash_directory, filename)
        encrypted_filepath = "{}/{}".format(self.cstash_directory, filename)
        self.gpg.encrypt_file(stream, self.key, armor=False, output=encrypted_filepath)

        return encrypted_filepath
