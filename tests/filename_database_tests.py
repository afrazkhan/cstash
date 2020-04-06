#!/usr/bin/env python3

import unittest
from sqlitedict import SqliteDict
import os
import shutil
import hashlib
import cstash.crypto.filenames as filenames

class TestFilenameDatabaseOperations(unittest.TestCase):
    """
    Test the Filenames class methods
    """

    def __init__(self, *args, **kwargs):
        """ Set some data to be used, such as key names for the database """

        super(TestFilenameDatabaseOperations, self).__init__(*args, **kwargs)
        self.test_files_directory = f"{os.getcwd()}/test_files"
        self.test_db_file = f"{self.test_files_directory}/filenames.sqlite"
        self.dummy_filename = "/home/dummy_user/dummy_filename"
        self.dummy_filename_hash = "dummy_filename_hash"
        self.dummy_cryptographer = "dummy_cryptographer"
        self.dummy_bucket_name = "dummy_bucket"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_file_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_file_path = f"{self.test_files_directory}/{self.single_file}"

    def setUp(self):
        """ Create test database with two entries from two test files """

        os.makedirs(self.test_files_directory, exist_ok=True)
        os.makedirs(self.two_directory_tieres, exist_ok=True)

        db_connection = SqliteDict(self.test_db_file, autocommit=True, flag='c')

        # Create two test files in two different directories, get their file
        # hashes, and stored them in the test database
        for this_directory in [self.test_files_directory, self.two_directory_tieres]:
            current_file = f"{this_directory}/{self.single_file}"
            with open(current_file, "w+") as test_file:
                test_file.write("Some amazing things, right here")

            sha256 = hashlib.sha256()
            with open(current_file, 'rb') as f:
                for block in iter(lambda: f.read(4096), b''):
                    sha256.update(block)
            current_hash = sha256.hexdigest()
            db_connection[current_file] = {
                "file_hash": current_hash,
                "cryptographer": self.dummy_cryptographer,
                "bucket": self.dummy_bucket_name
            }

        self.two_directory_tieres_file_hash = db_connection[self.two_directory_tieres_file_path]["file_hash"]
        self.single_directory_file_hash = db_connection[self.single_directory_file_path]["file_hash"]

        self.search_cases = {
            "single_directory_exact": (True, self.single_directory_file_path, self.single_directory_file_hash),
            "single_directory_fuzzy": (False, self.single_directory_file_path, self.single_directory_file_hash),
            "two_directories_exact": (True, self.two_directory_tieres_file_path, self.two_directory_tieres_file_hash),
            "two_directories_fuzzy": (False, self.two_directory_tieres_file_path, self.two_directory_tieres_file_hash)
        }

        self.search_cases_non_existant = {
            "single_directory_exact": (True, "/should_not_exist"),
            "single_directory_fuzzy": (False, "/should_not_exist"),
            "three_directory_exact": (True, "/should/not/exist"),
            "three_directory_fuzzy": (False, "/should/not/exist")
        }

        db_connection.close()

    def tearDown(self):
        """ Delete test fixture files """

        shutil.rmtree(self.test_files_directory)

    def test_search_existing_record(self):
        """
        Search for an existing record with permutations of fuzziness, and directory levels.

        Should return a list with a single element containing the existing record in all cases.
        """

        files_db = filenames.Filenames(self.test_files_directory)

        for name, (exact, this_path, this_hash) in self.search_cases.items():
            with self.subTest(name=name):
                result = files_db.search(obj=this_path, exact=exact)
                self.assertTrue(result == [(
                        this_path,
                        {
                            "file_hash": this_hash,
                            "cryptographer": self.dummy_cryptographer,
                            "bucket": self.dummy_bucket_name
                        }
                    )])

    def test_search_non_existent_record(self):
        """
        Search for a non existing record with permutations of fuzziness, and directory levels.

        Should return an empty list in all cases.
        """

        files_db = filenames.Filenames(self.test_files_directory)

        for name, (exact, this_path) in self.search_cases_non_existant.items():
            with self.subTest(name=name):
                result = files_db.search(obj=this_path, exact=exact)
                self.assertTrue(result == [])

    def test_existing_hash_existing(self):
        """
        Hash a dummy file, and see if the hash exists in the database.

        Should return true in all cases.
        """

        files_db = filenames.Filenames(self.test_files_directory)

        self.assertTrue(files_db.existing_hash(self.single_directory_file_path))
        self.assertTrue(files_db.existing_hash(self.two_directory_tieres_file_path))

if __name__ == "__main__":
    unittest.main()
