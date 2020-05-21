#!/usr/bin/env python3

"""
Unit tests for the Config class
"""

import unittest
import os
import shutil
from cstash.config.config import Config

class TestConfigOperations(unittest.TestCase):
    """
    Tests for configuration file operations
    """

    def __init__(self, *args, **kwargs):
        """ Set the paths to be used """

        super(TestConfigOperations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.config_files_as_dicts = {
            "all_options_set": {
                "cryptographer": "gpg",
                "storage_provider": "s3",
                "key": "somemadkey",
                "bucket": "test_bucket"
            },
            "some_options_set": {
                "cryptographer": "gpg",
                "storage_provider": "s3",
            },
            "no_options_set": {}
        }

    def setUp(self):
        """ Create known path structures on disk to run tests against """

        os.makedirs(self.test_files_directory, exist_ok=True)

        self.config_files_as_strings = {}

        # For each dict of options, construct the expected content in the file as a
        # string for testing against
        for this_config_file in self.config_files_as_dicts:
            full_option_list = ["cryptographer", "storage_provider", "key", "bucket"]
            self.config_files_as_strings[this_config_file] = "[default]"
            for given_option in self.config_files_as_dicts[this_config_file].items():
                if given_option[0] in full_option_list:
                    self.config_files_as_strings[this_config_file] = f"{self.config_files_as_strings[this_config_file]}\n" + \
                        f"{given_option[0]} = {self.config_files_as_dicts[this_config_file][given_option[0]]}"

    def tearDown(self):
        """ Delete test fixture files """

        shutil.rmtree(self.test_files_directory)

    def test_set_values(self):
        """ Set a single value in the configuration file """

        # Write the config files using the real function
        for this_config_file in self.config_files_as_dicts:
            config = Config(self.test_files_directory, this_config_file)
            config.write("default", self.config_files_as_dicts[this_config_file])

        # Compare the files created with strings created from the same dicts
        for this_config_set in self.config_files_as_strings:
            result = open(f"{self.test_files_directory}/{this_config_set}", "r").read().rstrip()
            self.assertTrue(result == self.config_files_as_strings[this_config_set], msg=f"{result} == {self.config_files_as_strings[this_config_set]}")

    def test_override_options(self):
        """
        Given dict_a and dict_b, dict_a should override key/values in dict_b. If any of the keys
        end up having a None value, that should raise a CstashCriticalException
        """

        print("TODO")

if __name__ == "__main__":
    unittest.main()
