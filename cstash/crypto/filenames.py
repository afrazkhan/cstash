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
        db = db or self.db
        db_connection = self.connect_to_db()

        if obj in db_connection:
            return db_connection[obj]

        db_connection.close()

        return False

    def store(self, obj, db=None):
        """
        If the filenames DB already has an entry for the object, return that, otherwise,
        create a new entry for the object and return that
        """

        existing_entry = self.search(obj)

        if existing_entry:
            logging.debug("Found existing entry for {} in DB".format(obj))
            return existing_entry
        else:
            logging.debug("No existing DB entry for {}, adding it".format(obj))

            db = db or self.db
            db_connection = self.connect_to_db()

            new_entry = secrets.token_urlsafe(nbytes=42)
            db_connection[obj] = new_entry
            db_connection.close()

            return new_entry

    def restore(self):
        """
        TODO: If we've accidentally deleted the DB file, recreate it by fetching all objects from S3,
        decrypt them, and writing their paths to the DB file again
        """

        return "TODO"
