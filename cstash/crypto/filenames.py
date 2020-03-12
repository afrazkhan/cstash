#!/usr/bin/env python3

from sqlitedict import SqliteDict
import secrets
from pathlib import Path
import logging

class Filenames():
    """
    Creates and manages filename obsfucation database
    """

    def __init__(self, cstash_directory, log_level):
        """ Create the cstash SQLite DB """

        logging.getLogger().setLevel(log_level)
        self.db = "{}/filenames.sqlite".format(cstash_directory)

    def connect_to_db(self, db=None):
        db = db or self.db

        return SqliteDict(db, autocommit=True, flag='c')

    def search(self, obj, db=None):
        """ Return key for [obj] in [db] if it exists, or False if not """

        db = db or self.db
        db_connection = self.connect_to_db()

        if obj in db_connection:
            return db_connection[obj]

        db_connection.close()

        return False

    def store(self, obj, db=None):
        """
        Create or overwrite an entry in the filenames [db] for mapping [obj] to an obsfucated name.

        Return a dict of [entry] denoting the obsfucated filename, and [db_connect] to be
        used later for closing the connection
        """

        db = db or self.db
        db_connection = self.connect_to_db(db)

        new_entry = secrets.token_urlsafe(nbytes=42)
        db_connection[obj] = new_entry
        logging.debug(db_connection[obj])

        return { 'entry': new_entry, 'db_connection': db_connection }

    def close_db_connection(self, db_connection):
        """
        Close the connection to [db_connection]. Used with store() so that we don't
        create entries that failed to upload
        """

        db_connection.close()

    def restore(self):
        """
        TODO: If we've accidentally deleted the DB file, recreate it by fetching all objects from S3,
        decrypt them, and writing their paths to the DB file again
        """

        return "TODO"
