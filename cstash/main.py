#!/usr/bin/env python3

import click
import os
from pathlib import Path

def create_cstash_directory():
    """ Ensure ~/.cstash directory exists and return it as a string """

    cstash_dir = "{}/.cstash".format(str(Path.home()))
    if not os.path.isdir(cstash_dir):
        os.mkdir(cstash_dir, mode=0o700)

    return cstash_dir

def get_config(cstash_directory):
    """ Return configuration from file, if present """

    config_file = f"{cstash_directory}/config"

    if os.path.isfile(config_file):
        with open(config_file, "r") as contents:
            return contents.read()

    return None

@click.group()
@click.option("--log-level", '-l', default="ERROR", type=click.Choice(["INFO", "ERROR", "DEBUG"]), help="How much information to show in logging. Default is ERROR")
@click.pass_context
def main(ctx=None, log_level="ERROR", cstash_directory=create_cstash_directory()):
    """ Create the ctx object to pass down to all other commands """

    cstash_directory = create_cstash_directory()
    config = get_config(cstash_directory)

    ctx.obj = {'log_level': log_level, 'cstash_directory': cstash_directory, 'config': config}

from cstash.storage.commands import search as search_command
main.add_command(search_command)

from cstash.crypto.commands import stash as stash_command
main.add_command(stash_command)

from cstash.crypto.commands import fetch as fetch_command
main.add_command(fetch_command)

if __name__ == "__main__":
    main()
