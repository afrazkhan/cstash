#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlitedict import SqliteDict
import secrets
from pathlib import Path
import cstash.libs.helpers as helpers
import cstash.libs.exceptions as exceptions
import logging
import hashlib

class FilenamesDatabase():
    """
    Creates and manages filename obsfucation database
    """

    def __init__(self, cstash_directory, log_level=None):
        """ Create the cstash SQLite DB """

        logging.getLogger().setLevel(level=log_level or "ERROR")
        self.db = "{}/filenames.sqlite".format(cstash_directory)

    def search(self, obj, exact=False, db=None):
        """
        Search the database for partial matches of [obj], and return a list of matches
        in the tuple form:

        ("obj", {"file_hash": string, "cryptographer": string, "storage_provider": string, "bucket": string})

        If [exact] == True, then only exact matches will be returned. Since there should
        only ever be a single exact match for a path in the DB, a CstashCriticalException
        will be thrown if more than a single element is in the resulting list. This shouldn't
        be possible anyway, since the DB is a key/value store, but it's a safety measure.
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=True, flag='r')
        if exact is True:
            keys = [(k, db_connection[k]) for k in db_connection.keys() if obj == k]
        else:
            keys = [(k, db_connection[k]) for k in db_connection.keys() if obj in k]

        if exact is True and len(keys) > 1:
            raise exceptions.CstashCriticalException(message=(f"Found more than a single match "
                  "for {obj} in the database:\n\n{keys}"))

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

        if existing_entry[0][1]['file_hash'] == new_hash:
            return True

        return False

    def store(self, obj, cryptographer, storage_provider, bucket, db=None):
        """
        Create or overwrite an entry in the filenames [db] for mapping [obj] to an obsfucated name.

        Return a dict of [entry] denoting the obsfucated filename, and [db_connection] to be
        used later for closing the connection
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=False, flag='c')

        new_entry = self.file_hash(obj)
        db_connection[obj] = {
            "file_hash": new_entry,
            "cryptographer": cryptographer,
            "storage_provider": storage_provider,
            "bucket": bucket }
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