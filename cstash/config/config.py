"""
Handle reading and writing Cstash configuration
"""

import configparser
import logging
import cstash.libs.exceptions as exceptions

class Config():
    def __init__(self, cstash_directory, config_file="config.ini", log_level="ERROR"):
        logging.getLogger().setLevel(log_level)
        self.config = configparser.ConfigParser()
        self.config_file = f"{cstash_directory}/{config_file}"

    def read(self, section="default"):
        """
        Read [section] from self.config_file and return it
        """

        self.config.read(self.config_file)
        return dict(self.config[section])

    def write(self, section="default", options={}):
        """
        Set any of the given values for [section] in the config file:
        [cstash_directory], [cryptographer], [storage_provider], [key], [bucket]
        """

        self.config.read(self.config_file)

        if section not in self.config.sections():
            self.config.add_section(section)

        for k, v in options.items():
            if v != None:
                self.config[section][k] = v

        with open(self.config_file, "+w") as config_file:
            self.config.write(config_file)
