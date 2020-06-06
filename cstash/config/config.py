"""
Handle reading and writing Cstash configuration
"""

import configparser
import os
import logging

class Config():
    def __init__(self, cstash_directory, config_file="config.ini", log_level=None): # pylint: disable=unused-argument
        self.config = configparser.ConfigParser()
        self.config_file = f"{cstash_directory}/{config_file}"

    def read(self, section="default"):
        """
        Read [section] from self.config_file and return it. Return a complete dictionary of
        keys with None values if there is no config file
        """

        self.config.read(self.config_file)
        try:
            if os.path.isfile(self.config_file):
                return dict(self.config[section])
        except KeyError:
            logging.info(f"A profile for {section} did not exist. Creating it now")
            self.config.add_section(section)
            with open(self.config_file, "+w") as config_file:
                self.config.write(config_file)

        return {
            "cryptographer": None,
            "storage_provider": None,
            "s3_endpoint_url": None,
            "s3_access_key": None,
            "s3_secret_access_key": None,
            "key": None,
            "bucket": None
        }

    def write(self, section="default", options={}):
        """
        Set any of the given values for [section] in the config file:
        [cstash_directory], [cryptographer], [storage_provider], [key], [bucket]
        """

        self.config.read(self.config_file)

        if section not in self.config.sections():
            self.config.add_section(section)

        for k, v in options.items():
            if v is not None:
                self.config[section][k] = v

        with open(self.config_file, "+w") as config_file:
            self.config.write(config_file)
        os.chmod(self.config_file, 0o600)
