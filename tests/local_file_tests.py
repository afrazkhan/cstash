#!/usr/bin/env python3

import unittest
import os
import shutil
from cstash.libs import helpers as helpers

class TestLocalFileOperations(unittest.TestCase):
    """
    Run tests around all of the methods which perform local file actions
    """

    def __init__(self, *args, **kwargs):
        """ Set the paths to be used """

        super(TestLocalFileOperations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_path = f"{self.test_files_directory}/{self.single_file}"

    def setUp(self):
        """ Create a known path structures on disk to run tests against """

        try:
            os.makedirs(self.test_files_directory, exist_ok=True)
            os.makedirs(self.two_directory_tieres, exist_ok=True)

            for this_directory in [self.test_files_directory, self.two_directory_tieres]:
                with open(f"{this_directory}/{self.single_file}", "w+") as test_file:
                    test_file.write("Some amazing things, right here")

        except Exception as e:
            print(f"Couldn't create fixture: {e}")

    def tearDown(self):
        """ Delete test fixture files """

        shutil.rmtree(self.test_files_directory)

    def test_get_paths_single_files(self):
        """ Test helpers.get_paths() with single files """

        for this_directory in  [self.test_files_directory, self.two_directory_tieres]:
            result = helpers.get_paths(f"{this_directory}/{self.single_file}")
            expected = [f"{this_directory}/{self.single_file}"]

            self.assertEqual(result, expected, msg="helpers.get_paths() failed to return " \
                "expected result when tested with a single file path")

    def test_get_paths_directories(self):
        """ Test helpers.get_paths() recursively, with files from subdirectories """

        result = helpers.get_paths(self.test_files_directory)
        expected = [self.single_directory_path, self.two_directory_tieres_path]

        self.assertEqual(result, expected, msg="helpers.get_paths() failed to return " \
            "expected result when tested with a directory")

if __name__ == "__main__":
    unittest.main()
