#!/usr/bin/env python3

import unittest
import os
import shutil
from cstash.crypto import crypto as crypto
import gnupg

class TestEncryptionOperations(unittest.TestCase):
    """
    Run integration tests for the Encryption class
    """

    def __init__(self, *args, **kwargs):
        """ Set the paths to be used """

        super(TestEncryptionOperations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_file_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_file_path = f"{self.test_files_directory}/{self.single_file}"
        self.gnupg_home = f"{self.test_files_directory}/.gnupg"
        self.gpg_password = "foobar"
        self.file_contents = "Some amazing things, right here"

    def setUp(self):
        """ Create a known path structures on disk to run tests against """

        try:
            os.makedirs(self.test_files_directory, exist_ok=True)
            os.makedirs(self.two_directory_tieres, exist_ok=True)
            os.makedirs(self.gnupg_home, exist_ok=True)

            for this_directory in [self.test_files_directory, self.two_directory_tieres]:
                with open(f"{this_directory}/{self.single_file}", "w+") as test_file:
                    test_file.write(self.file_contents)
                    test_file.close()

            self.gpg = gnupg.GPG(gnupghome=self.gnupg_home)
            with open(f"{self.gnupg_home}/gpg-agent.conf", "w+") as gpg_configuration:
                gpg_configuration.write("pinentry-program /usr/bin/pinentry-tty")
                gpg_configuration.close()

            gpg_key_id = f"{self.gpg.gen_key(self.gpg.gen_key_input(passphrase=self.gpg_password))}"

            self.encryption_cases = {
                "gpg_single_file": ("gpg", self.single_directory_file_path, gpg_key_id)
            }


        except Exception as e:
            print(f"Couldn't create fixture: {e}")

    def tearDown(self):
        """ Delete test fixture files """

        shutil.rmtree(self.test_files_directory)

    def test_encrypt_decrypt(self):
        """
        Test encrypt() with all our cryptographers
        """

        for name, (cryptographer, source_file, key) in self.encryption_cases.items():
            with self.subTest(name=name):
                encryption = crypto.Encryption(
                    cstash_directory=self.test_files_directory,
                    cryptographer=cryptographer,
                    extra_args={"gnupg_home": self.gnupg_home})
                encryption.encrypt(source_file, f"{os.path.split(source_file)[1]}.gpg", key)

                decrypted_file = encryption.decrypt(
                    filepath=f"{source_file}.gpg",
                    destination=f"{source_file}_decrypted",
                    password=self.gpg_password)
                decrypted_file_contents = open(decrypted_file, "r").read()

                self.assertEqual(self.file_contents, decrypted_file_contents)

if __name__ == "__main__":
    unittest.main()
