#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlitedict import SqliteDict
import secrets
from pathlib import Path
import cstash.libs.helpers as helpers
import logging

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
        in the tuple form: ("obj", {"obsfucated name", "cryptographer"})
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=True, flag='r')
        keys = [(k, db_connection[k]) for k in db_connection.keys() if obj in k]

        db_connection.close()

        return keys

    def store(self, obj, cryptographer, db=None):
        """
        Create or overwrite an entry in the filenames [db] for mapping [obj] to an obsfucated name.

        Return a dict of [entry] denoting the obsfucated filename, and [db_connect] to be
        used later for closing the connection
        """

        db = db or self.db
        db_connection = SqliteDict(db, autocommit=False, flag='c')

        new_entry = secrets.token_urlsafe(nbytes=42)
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
