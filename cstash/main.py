#!/usr/bin/env python3

import click
import os
from cstash.config.config import Config
from pathlib import Path
from cstash.libs import helpers as helpers

helpers.set_logger()

def create_cstash_directory():
    """ Ensure ~/.cstash directory exists and return it as a string """

    cstash_dir = "{}/.cstash".format(str(Path.home()))
    if not os.path.isdir(cstash_dir):
        os.mkdir(cstash_dir, mode=0o700)

    return cstash_dir

@click.group()
@click.option("--log-level", '-l', default="ERROR", type=click.Choice(["INFO", "ERROR", "DEBUG"], case_sensitive=False), help="How much information to show in logging. Default is ERROR")
@click.pass_context
def main(ctx=None, log_level="ERROR", cstash_directory=create_cstash_directory()):
    """ Create the ctx object to pass down to all other commands """

    cstash_directory = create_cstash_directory()
    config = Config(cstash_directory).read()

    ctx.obj = {'log_level': log_level.upper(), 'cstash_directory': cstash_directory, 'config': config}

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

if __name__ == "__main__":
    main()
