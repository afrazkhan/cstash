#!/usr/bin/env python3

# Queues:  https://github.com/peter-wangxu/persist-queue
# Threads: https://realpython.com/intro-to-python-threading/#starting-a-thread

import time
import logging
import os
import daemon
import daemon.pidfile
import psutil
import persistqueue
import threading
from cstash.crypto.filenames_database import FilenamesDatabase
from cstash.crypto.commands import stash
from cstash.libs import helpers
from cstash.libs import exceptions

class Daemon():
    def __init__(self, cstash_directory, log_level, click_context):
        self.cstash_directory = cstash_directory
        self.log_file = open(f"{cstash_directory}/cstash.log", "w+")
        self.pid_file = f"{self.cstash_directory}/cstash-daemon.pid"
        self.queue_location = f"{self.cstash_directory}/reprocess-queue"
        self.click_context = click_context

    def reload_files_to_watch(self):
        """
        Return a list of files to watch from the filesnames database
        """

        files_to_watch = FilenamesDatabase(self.cstash_directory).return_all_entries()
        logging.debug(f"Reloaded database: {files_to_watch}")

        return files_to_watch

    def process_queue(self):
        """ Pop queue and send it to the stash() click command for processeing """

        logging.info("Starting queue processor")

        reprocess_queue = persistqueue.UniqueQ(self.queue_location)

        i = 0
        while i < reprocess_queue.size:
            logging.info(reprocess_queue.size)
            this_file = reprocess_queue.get()
            logging.info(f"{this_file} was received for the queue. It is now being sent for processing")
            stash.callback(None, None, None, None, True, this_file)
            i+=1

    def populate_queue(self):
        """
        Reload the entries from the filesnames database every 5 seconds, and monitor file changes by
        comparing the modified time in the database with that of the current modification time. Trigger
        a re-upload on modification time mismatch
        """

        entries = self.reload_files_to_watch()
        for e in entries:
            if not os.path.isfile(e):
                continue
            if entries[e]["mtime"] < os.stat(e).st_mtime:
                logging.info(f"{e} changed. It will be queued for re-uploading")
                reprocess_queue = persistqueue.UniqueQ(self.queue_location)
                reprocess_queue.put(e)

    def start(self):
        """ Bootstrap the daemon process """

        print("BEWARE: The daemon is experimental. If it explodes, it will be without warning")

        try:
            logger = logging.getLogger()

            # Needed so we don't lose the Click() context
            def process_wrapper():
                with self.click_context:
                    self.process_queue()

            def populate_wrapper():
                with self.click_context:
                    self.populate_queue()

            with daemon.DaemonContext(
                pidfile=daemon.pidfile.PIDLockFile(self.pid_file),
                files_preserve=[logger.handlers[0].stream.fileno()],
                stderr=self.log_file,
                stdout=self.log_file
            ):
                logging.info("Started cstash daemon")

                while True:
                    threading.Thread(target=process_wrapper).start()
                    time.sleep(5)
                    threading.Thread(target=populate_wrapper).start()

        except Exception as e:
            print(f"Couldn't start the daemon: {e}")

    def stop(self):
        """ Kill the process from [self.pid_file], and delete that file """

        logging.info("Stopping daemon")
        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read())

            try:
                psutil.Process(pid).kill()
            except psutil.NoSuchProcess:
                pass

            os.remove(self.pid_file)
        except FileNotFoundError:
            logging.info(f"Pid file {self.pid_file} not found")
            pass
