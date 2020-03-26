#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlitedict import SqliteDict
import secrets
from pathlib import Path
import cstash.libs.helpers as helpers
import logging
import hashlib

class Filenames():
    """
    Creates and manages filename obsfucation database
    """

    def __init__(self, cstash_directory, log_level=None):
        """ Create the cstash SQLite DB """

        helpers.set_logger(level=log_level)
        self.db = "{}/filenames.sqlite".format(cstash_directory)

    def search(self, obj, db=None):
        """
        Search the database for partial matches of [obj], and return a list of matches
        in the tuple form: ("obj", {"obsfucated name": string, "cryptographer": string})
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=True, flag='r')
        keys = [(k, db_connection[k]) for k in db_connection.keys() if obj in k]

        db_connection.close()

        return keys

    def file_hash(self, filepath):
        """
        Return the sha256 hash for [filepath], or False on failure
        """

        try:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for block in iter(lambda: f.read(4096), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            logging.error("Couldn't hash the file {}: {}".format(filepath, e))
            return False

    def existing_hash(self, filepath):
        """
        Check if the hash for [filepath] is the same as the one in the database.

        Return True if it's the same, False if not
        """

        new_hash = self.file_hash(filepath)
        existing_entry = self.search(filepath)

        if len(existing_entry) == 0:
            return False

        if existing_entry[0][1]['obsfucated_name'] == new_hash:
            return True

        return False

    def store(self, obj, cryptographer, db=None):
        """
        Create or overwrite an entry in the filenames [db] for mapping [obj] to an obsfucated name.

        Return a dict of [entry] denoting the obsfucated filename, and [db_connect] to be
        used later for closing the connection
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=False, flag='c')

        new_entry = self.file_hash(obj)
        db_connection[obj] = { "obsfucated_name": new_entry, "cryptographer": cryptographer }
        logging.debug("Wrote {} to database".format(db_connection[obj]))

        return { 'entry': new_entry, 'db_connection': db_connection }

    def close_db_connection(self, db_connection):
        """
        Close the connection to [db_connection]. Used with store() so that we don't
        create entries that failed to upload
        """

        db_connection.commit()
        db_connection.close()

    def restore(self):
        """
        TODO: If we've accidentally deleted the DB file, recreate it by fetching all objects from S3,
        decrypt them, and writing their paths to the DB file again
        """

        return "TODO"
