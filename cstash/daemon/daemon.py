#!/usr/bin/env python3

import time
import logging
import os
import daemon
import daemon.pidfile
import psutil
from cstash.crypto.filenames_database import FilenamesDatabase
from cstash.crypto.commands import stash

class Daemon():
    def __init__(self, cstash_directory, log_level):
        logging.getLogger().setLevel(log_level)
        self.cstash_directory = cstash_directory
        self.log_file = open(f"{cstash_directory}/cstash.log", "+w")
        self.pid_file = f"{self.cstash_directory}/cstash-daemon.pid"

    def get_files_to_watch(self):
        """
        Get a list of files to watch
        """

        files_to_watch = FilenamesDatabase(self.cstash_directory).list_all_entries()
        files_to_watch.append(f"{self.cstash_directory}/filenames.sqlite")

        return files_to_watch

    def watch_files(self, files):
        """
        Given a list as [files], watch for modification every 5 seconds, and trigger
        actions on modification of those files. Reload the list if the database changes
        """

        file_states = {}
        while True:
            for f in files:
                if not os.path.isfile(f):
                    continue
                try:
                    if file_states[f] < os.stat(f).st_mtime:
                        if f == f"{self.cstash_directory}/filenames.sqlite":
                            files = self.get_files_to_watch()
                            logging.info("Reloaded files to watch from database")
                            continue

                        logging.info(f"{f} changed. It will be re-uploaded")
                        self.re_upload(f)
                except KeyError:
                    pass

                file_states[f] = os.stat(f).st_mtime

            time.sleep(5)

    def re_upload(self, this_file):
        """
        Encrypt and re-upload [this_file]
        """

        logging.info(f"Re-uploading {this_file}")
        stash.callback(None, None, None, None, True, this_file)

    def start(self):
        """ Bootstrap the daemon process """

        try:
            with daemon.DaemonContext(
                pidfile=daemon.pidfile.PIDLockFile(self.pid_file),
                stderr=self.log_file,
                stdout=self.log_file
            ):
                files_to_watch = self.get_files_to_watch()
                self.watch_files(files_to_watch)
        except Exception as e:
            print(f"Couldn't start the daemon: {e}")

    def stop(self):
        """ Kill the process from [self.pid_file], and delete that file """

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read())

            try:
                psutil.Process(pid).kill()
            except psutil.NoSuchProcess:
                pass

            os.remove(self.pid_file)
        except FileNotFoundError:
            pass
