#!/usr/bin/env python3

"""
Entry point for the CLI application
"""

import click
import os
from cstash.config.config import Config
from pathlib import Path
from cstash.libs import helpers
import logging

def create_cstash_directory():
    """ Ensure ~/.cstash directory exists and return it as a string """

    cstash_dir = "{}/.cstash".format(str(Path.home()))
    if not os.path.isdir(cstash_dir):
        os.mkdir(cstash_dir, mode=0o700)

    return cstash_dir

@click.group()
@click.option("--profile", '-p', default='default', help='The configuration profile to use')
@click.option("--log-level", '-l', default="ERROR", type=click.Choice(["INFO", "ERROR", "DEBUG"], case_sensitive=False), help="How much information to show in logging. Default is ERROR")
@click.pass_context
def main(ctx=None, profile='default', log_level="ERROR", cstash_directory=create_cstash_directory(),):
    """
    Stash and fetch encrypted versions of your files to your choice of storage providers
    \f

    This function does nothing by itself, and only creates the ctx object to pass down to all
    other commands
    """

    helpers.set_logger(level=log_level.upper(), filename=f"{cstash_directory}/cstash.log")
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    cstash_directory = create_cstash_directory()
    config = Config(cstash_directory).read(section=profile)

    ctx.obj = {
        'profile': profile,
        'log_level': log_level.upper(),
        'cstash_directory': cstash_directory,
        'config': config
    }

@main.command()
@click.pass_context
def initialise(ctx):
    """ Initialise a default key, which is necessary for the database backup """

    from cstash.crypto.pcrypt import PCrypt
    encryptor = PCrypt(cstash_directory=ctx.obj.get("cstash_directory"),
                       log_level=ctx.obj.get("log_level"))

    encryptor.generate_key("default")

from cstash.storage.commands import storage as storage_commands
main.add_command(storage_commands)

from cstash.crypto.commands import stash as stash_command
main.add_command(stash_command)

from cstash.crypto.commands import fetch as fetch_command
main.add_command(fetch_command)

from cstash.crypto.commands import database as database_commands
main.add_command(database_commands)

from cstash.config.commands import config as config_command
main.add_command(config_command)

from cstash.daemon.commands import daemon as daemon_command
main.add_command(daemon_command)

if __name__ == "__main__":
    main()
