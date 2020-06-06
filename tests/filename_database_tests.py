#!/usr/bin/env python3

"""
Unit tests for the Filenames class
"""

import unittest
from sqlitedict import SqliteDict
import os
import shutil
import hashlib
import cstash.crypto.filenames_database as filenames

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
        self.dummy_key = "dummy_key"
        self.dummy_bucket_name = "dummy_bucket"
        self.two_directory_tieres = f"{self.test_files_directory}/one/two"
        self.single_file = "foobar.txt"
        self.two_directory_tieres_file_path = f"{self.two_directory_tieres}/{self.single_file}"
        self.single_directory_file_path = f"{self.test_files_directory}/{self.single_file}"
        self.storage_provider = "s3"
        self.dummy_endpoint_url = "https://s3.amazonaws.com"

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
            sha256.update(bytes(f"{current_file}", encoding="utf-8"))
            current_hash = sha256.hexdigest()

            db_connection[current_file] = {
                "filename_hash": current_hash,
                "cryptographer": self.dummy_cryptographer,
                "bucket": self.dummy_bucket_name
            }

        self.two_directory_tieres_filename_hash = db_connection[self.two_directory_tieres_file_path]["filename_hash"]
        self.single_directory_filename_hash = db_connection[self.single_directory_file_path]["filename_hash"]

        self.search_cases = {
            "single_directory_exact": (
                True, self.single_directory_file_path, self.single_directory_filename_hash),
            "single_directory_fuzzy": (
                False, self.single_directory_file_path, self.single_directory_filename_hash),
            "two_directories_exact": (
                True, self.two_directory_tieres_file_path, self.two_directory_tieres_filename_hash),
            "two_directories_fuzzy": (
                False, self.two_directory_tieres_file_path, self.two_directory_tieres_filename_hash)
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
        Test search() by searching for an existing record with permutations of fuzziness,
        and directory levels.

        Should return a list with a single element containing the existing record in all cases.
        """

        files_db = filenames.FilenamesDatabase(self.test_files_directory)

        for name, (exact, this_path, this_hash) in self.search_cases.items():
            with self.subTest(name=name):
                result = files_db.search(obj=this_path, exact=exact)
                self.assertTrue(result == [(
                    this_path,
                    {
                        "filename_hash": this_hash,
                        "cryptographer": self.dummy_cryptographer,
                        "bucket": self.dummy_bucket_name
                    }
                    )])

    def test_search_non_existent_record(self):
        """
        Test search() by searching for a non existing record with permutations of
        fuzziness, and directory levels.

        Should return an empty list in all cases.
        """

        files_db = filenames.FilenamesDatabase(self.test_files_directory)

        for name, (exact, this_path) in self.search_cases_non_existant.items():
            with self.subTest(name=name):
                result = files_db.search(obj=this_path, exact=exact)
                self.assertTrue(result == [])

    def test_existing_hash(self):
        """
        Test existing_hash() by searching for both known entries that should exist
        in the database, and made up entries that shouldn't.

        Should return True for known entries, and False for made up entries.
        """

        files_db = filenames.FilenamesDatabase(self.test_files_directory)

        self.assertTrue(files_db.existing_hash(self.single_directory_file_path))
        self.assertTrue(files_db.existing_hash(self.two_directory_tieres_file_path))
        self.assertFalse(files_db.existing_hash("boogada"))

    def test_store_and_close(self):
        """
        Store an entry in the database using store(), then close the connection using
        close_db_connection()
        """

        files_db = filenames.FilenamesDatabase(self.test_files_directory)

        result = files_db.store(
            obj=self.single_directory_file_path,
            cryptographer=self.dummy_cryptographer,
            key=self.dummy_key,
            storage_provider=self.storage_provider,
            s3_endpoint_url=self.dummy_endpoint_url,
            bucket=self.dummy_bucket_name
        )

        # TODO: Check the entry itself in some low-level way
        self.assertTrue("entry" in result and "db_connection" in result)

        files_db.close_db_connection(result["db_connection"])

    def test_store_close_and_search(self):
        """
        Store an entry with store(), then use search() to find that entry. Also verify
        the hash with one we calculate here.
        """

        files_db = filenames.FilenamesDatabase(self.test_files_directory)

        store_result = files_db.store(
            obj=self.single_directory_file_path,
            cryptographer=self.dummy_cryptographer,
            key=self.dummy_key,
            storage_provider=self.storage_provider,
            s3_endpoint_url=self.dummy_endpoint_url,
            bucket=self.dummy_bucket_name
        )

        search_result = files_db.search(obj=self.single_directory_file_path, exact=True)

        self.assertTrue(store_result["entry"] == search_result[0][1]["filename_hash"],
                        msg=f"store_result = {store_result}\n" \
                        f"search_result = {search_result}")

        # Calculate the file hash ourselves, to check it with what's stored
        sha256 = hashlib.sha256()
        sha256.update(bytes(f"{self.single_directory_file_path}", encoding="utf-8"))
        correct_hash = sha256.hexdigest()

        self.assertTrue(store_result["entry"] == correct_hash)
        self.assertTrue(search_result[0][1]["filename_hash"] == correct_hash)

        files_db.close_db_connection(store_result["db_connection"])

if __name__ == "__main__":
    unittest.main()
