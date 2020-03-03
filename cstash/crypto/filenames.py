#!/usr/bin/env python3

from sqlitedict import SqliteDict
import secrets
from pathlib import Path

class Filenames():
    """
    Creates and manages filename obsfucation database
    """

    def __init__(self, cstash_directory):
        """ Create the cstash SQLite DB """

        self.filenames_db = SqliteDict(cstash_directory + '/filenames.sqlite', autocommit=True, flag='c')

    def search(self, obj):
        if obj in self.filenames_db:
            return self.filenames_db[obj]

        return False

    def store(self, obj):
        """
        If the filenames DB already has an entry for the object, return that, otherwise,
        create a new entry for the object and return that
        """

        existing_entry = self.search(obj)

        if existing_entry:
            return existing_entry
        else:
            new_entry = secrets.token_urlsafe(nbytes=42)
            self.filenames_db[obj] = new_entry

            return new_entry

    def restore(self):
        """
        TODO: If we've accidentally deleted the DB file, recreate it by fetching all objects from S3,
        decrypt them, and writing their paths to the DB file again
        """

        return "TODO"
