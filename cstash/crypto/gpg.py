"""
Use 'gnupg' module to call GPG binary for encryption/decryption tasks
"""

import logging
import gnupg
import os

class GPG():
    def __init__(self, cstash_directory, log_level=None, gnupg_home=None): # pylint: disable=unused-argument
        self.cstash_directory = cstash_directory
        self.gpg = gnupg.GPG(gnupghome=gnupg_home or f"{os.path.expanduser('~')}/.gnupg")

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

    def decrypt(self, filepath, destination, key, password=None): # pylint: disable=unused-argument
        """
        Decrypt [filepath] to [destination], and return the path to the decrypted file
        on success, or False on failure
        """

        try:
            stream = open(filepath, "rb")
            # TODO: Might it be nicer to default to the user's home directory on 'destination' failure?
            encrypted_filepath = destination or f"{filepath}.decrypted"
            self.gpg.decrypt_file(stream, output=encrypted_filepath, passphrase=password)
        except Exception as e:
            logging.error("Coudln't decrypt {}: {}".format(filepath, e))
            return False

        return encrypted_filepath
