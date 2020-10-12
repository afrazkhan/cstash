#!/usr/bin/env python3

"""
Integration tests for everything
"""

import unittest
import os
import shutil
from cstash.crypto import crypto
import gnupg
# import cryptography
from cryptography.fernet import Fernet
import boto3
from moto import mock_s3

@mock_s3
class TestIntegrations(unittest.TestCase):
    """
    Run integration tests for the Encryption class
    """

    def __init__(self, *args, **kwargs):
        """ Set the paths to be used """

        super(TestIntegrations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_file_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_file_path = f"{self.test_files_directory}/{self.single_file}"
        self.gnupg_home = f"{self.test_files_directory}/.gnupg"
        self.gpg_password = "foobar"
        self.file_contents = "Some amazing things, right here"
        self.test_bucket_name = "test-bucket"
        self.storage_cases = {
            "s3_existing_bucket": (
                "s3",
                self.test_bucket_name,
                self.single_directory_file_path,
                f"{self.test_files_directory}/{self.single_file}",
                "foo",
                "bar"
                ),
            "s3_existing_bucket_directory_destination": (
                "s3",
                self.test_bucket_name,
                self.single_directory_file_path,
                f"{self.test_files_directory}",
                "foo",
                "bar"
                ),
            "s3_existing_bucket_no_destination": (
                "s3",
                self.test_bucket_name,
                self.single_directory_file_path,
                None,
                "foo",
                "bar"
                )
        }

    def setUp(self):
        """ Create known path structures on disk to run tests against """

        os.makedirs(self.test_files_directory, exist_ok=True)
        os.makedirs(self.two_directory_tieres, exist_ok=True)
        os.makedirs(self.gnupg_home, exist_ok=True)

        s3_resource = boto3.resource('s3', region_name='eu-west-1')
        s3_resource.create_bucket(Bucket=self.test_bucket_name) # pylint: disable=no-member

        for this_directory in [self.test_files_directory, self.two_directory_tieres]:
            with open(f"{this_directory}/{self.single_file}", "w+") as test_file:
                test_file.write(self.file_contents)
                test_file.close()

        self.gpg = gnupg.GPG(gnupghome=self.gnupg_home)
        with open(f"{self.gnupg_home}/gpg-agent.conf", "w+") as gpg_configuration:
            gpg_configuration.write("pinentry-program /usr/bin/pinentry-tty")
            gpg_configuration.close()

        gpg_key_id = f"{self.gpg.gen_key(self.gpg.gen_key_input(passphrase=self.gpg_password))}"
        fernet_key = Fernet.generate_key()

        self.encryption_cases = {
            "gpg_single_file": ("gpg", self.single_directory_file_path, gpg_key_id, {"gnupg_home": self.gnupg_home}),
            "pcrypt_single_file": ("python", self.single_directory_file_path, fernet_key, None)
        }

    def tearDown(self):
        """ Delete test fixture files """

        shutil.rmtree(self.test_files_directory)
        try:
            os.remove(f"{os.path.curdir}/foobar.txt")
        except OSError:
            pass

    def test_encrypt_decrypt(self):
        """
        Test encrypt() and decrypt() with all our cryptographers
        """

        for name, (cryptographer, source_file, key, extra_args) in self.encryption_cases.items():
            with self.subTest(name=name):
                encryption = crypto.Encryption(
                    cstash_directory=self.test_files_directory,
                    cryptographer=cryptographer,
                    extra_args=extra_args)

                encryption.encrypt(source_file, f"{os.path.split(source_file)[1]}_encrypted", key)

                decrypted_file = encryption.decrypt(
                    filepath=f"{source_file}_encrypted",
                    destination=f"{source_file}_decrypted",
                    key=key,
                    password=self.gpg_password)
                decrypted_file_contents = open(decrypted_file, "r").read()

                self.assertEqual(self.file_contents, decrypted_file_contents)

    def test_upload_download_object(self):
        """
        Test Storage.upload() and Storage.download() with all our storage providers,
        and some permutations of arguments to storage.download()
        """

        for name, (storage_provider, bucket, test_file, destination, s3_access_key_id, s3_secret_access_key) in self.storage_cases.items():
            with self.subTest(name=name):
                from cstash.storage.storage import Storage
                Storage(storage_provider, s3_access_key_id, s3_secret_access_key).upload(bucket, test_file)
                retrieved_file = Storage(storage_provider, s3_access_key_id, s3_secret_access_key).download(bucket, self.single_file, destination)

                retrieved_file_contents = open(retrieved_file, "r").read()
                self.assertEqual(self.file_contents, retrieved_file_contents)

    def test_complete_functionality(self):
        """
        Full integration test:

        1. Hash filename
        2. Encrypt file to hashed name
        3. Upload to remote storage
        4. Download from remote storage
        5. Decrypt downloaded file (to new name)
        6. Check the files are the same
        """

        return "TODO"

if __name__ == "__main__":
    unittest.main()
