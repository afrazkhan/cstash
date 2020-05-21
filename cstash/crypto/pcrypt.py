"""
Cryptography functions supplied via native Python libraries
"""

import logging
from cryptography.fernet import Fernet
import os

class PCrypt():
    def __init__(self, cstash_directory, log_level=None): # pylint: disable=unused-argument
        self.cstash_directory = cstash_directory
        self.keys_directory = f"{self.cstash_directory}/keys"

    def generate_key(self, key_name):
        """
        Generate a new Fernet key, and return it as a byte object
        """

        try:
            os.makedirs(mode=0o700, name=self.keys_directory)
        except FileExistsError:
            pass

        key_file = f"{self.keys_directory}/{key_name}"

        if os.path.isfile(key_file):
            logging.error("Key already exists, not overwriting it")
            import sys
            sys.exit(1)

        key = Fernet.generate_key()
        with open(key_file, "wb") as key_file_writer:
            key_file_writer.write(key)
        os.chmod(key_file, 0o600)

        return key

    def get_key(self, key_name):
        """
        Ensure that [key_name] exists, and return it as a byte object. If the key
        had to be generated, also write it to [self.key_directory]/[key_name]
        """

        if not os.path.isfile(f"{self.keys_directory}/{key_name}"):
            fernet_key = self.generate_key(key_name)
        else:
            with open(f"{self.keys_directory}/{key_name}", "rb") as fernet_key_file:
                fernet_key = fernet_key_file.read()

        return fernet_key

    def encrypt(self, source_filepath, key, destination_filepath):
        """
        Encrypt [source_filepath] to [destination_filepath].

        Return [destination_filepath] for success or False for failure.
        """

        try:
            fernet = Fernet(self.get_key(key))

            with open(source_filepath, "rb") as source_data_file:
                source_data = source_data_file.read()
                encrypted_file_contents = fernet.encrypt(source_data)

            with open(destination_filepath, "wb+") as destination_file:
                destination_file.write(encrypted_file_contents)
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
            fernet = Fernet(self.get_key(key))

            with open(filepath) as file_contents:
                contents = file_contents.read()

            decrypted_contents = fernet.decrypt(contents.encode())

            destination_file = destination or f"{filepath}.decrypted"
            with open(destination, "w+") as destination_file:
                destination_file.write(decrypted_contents.decode())

        except Exception as e:
            logging.error("Coudln't decrypt {}: {}".format(filepath, e))
            return False

        return destination_file
