"""
Unit tests for the helper module
"""

#!/usr/bin/env python3

import unittest
import os
import shutil
from cstash.libs import helpers

class TestHelperOperations(unittest.TestCase):
    """
    Test the functions found in libs.helpers. These mostly revolve around local
    file operations
    """

    def __init__(self, *args, **kwargs):
        """ Set the paths to be used """

        super(TestHelperOperations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_file_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_file_path = f"{self.test_files_directory}/{self.single_file}"

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
        """
        Test helpers.get_paths() with single files.

        Should return the absolute path to the paths past
        """

        for this_directory in  [self.test_files_directory, self.two_directory_tieres]:
            result = helpers.get_paths(f"{this_directory}/{self.single_file}")
            expected = [f"{this_directory}/{self.single_file}"]

            self.assertEqual(result, expected, msg="helpers.get_paths() failed to return " \
                "expected result when tested with a single file path")

    def test_get_paths_directories(self):
        """
        Test helpers.get_paths() recursively, with a directory that has subdirectories.

        Should return absolute paths to all files found recursively
        """

        result = helpers.get_paths(self.test_files_directory)
        expected = [self.single_directory_file_path, self.two_directory_tieres_file_path]

        self.assertEqual(result, expected, msg="helpers.get_paths() failed to return " \
            "expected result when tested with a directory")

    def test_strip_path_with_file(self):
        """
        Pass valid file file path to helpers.strip_path()

        Should return a tuple with absolute path to the directory as the first element, and
        the file name as the second element
        """

        result = helpers.strip_path(self.single_directory_file_path)

        self.assertTrue(os.path.isdir(result[0]), msg=f"{result[0]} is not a directory")
        self.assertTrue(os.path.isfile(f"{result[0]}/{result[1]}"), msg=f"{result[1]} is not a file")

    def test_strip_path_with_directory(self):
        """
        Pass directory path to helpers.strip_path()

        Should return the directory as the first element, and a blank string as the second element
        """

        result = helpers.strip_path(self.test_files_directory)
        self.assertEqual(result[1], '', msg=f"{result[1]} should have been ''")

    def test_clear_path_directory(self):
        """
        Pass a directory to to helpers.clear_path instead of a file path.

        Should ultimately raise a SystemExit, and an exit code of 1
        """

        with self.assertRaises(SystemExit) as system_exit:
            helpers.clear_path(self.test_files_directory)

        self.assertEqual(system_exit.exception.code, 1, msg=f"{system_exit.exception.code} " \
            "should have been 1")

    def test_clear_path_already_clear(self):
        """
        Pass an already clear path to helpers.clear_path()

        Should return the absolute path to the non-existant file
        """

        result = helpers.clear_path(f"{self.test_files_directory}/non_existant_file")
        self.assertEqual(result, f"{self.test_files_directory}/non_existant_file")

    def test_clear_path_non_clear(self):
        """
        Pass a path to an existing file to helpers.clear_path()

        Should return the absolute path: "/path/to/file/[file].1.[file_extension]", where
        n is however many numbers it takes to avoid name collisions with existing files
        """

        result = helpers.clear_path(self.single_directory_file_path)
        self.assertEqual(result, f"{self.test_files_directory}/foobar.1.txt")

        c = 1
        while c < 3:
            with open(f"{self.test_files_directory}/foobar.{c}.txt", "w+") as test_file:
                test_file.write("Some amazing things, right here")

            result = helpers.clear_path(self.single_directory_file_path)
            c += 1
            self.assertEqual(result, f"{self.test_files_directory}/foobar.{c}.txt")

    def test_clear_path_non_path(self):
        """
        Pass a file path with non-existant parent directories.

        Should return the absolute path to the file, having created the necessary
        directories.
        """

        result = helpers.clear_path(f"{self.test_files_directory}/no/paths/here/foobar.txt")
        self.assertEqual(result, f"{self.test_files_directory}/no/paths/here/foobar.txt")
        self.assertTrue(os.path.exists(f"{self.test_files_directory}/no/paths/here/"))

if __name__ == "__main__":
    unittest.main()
