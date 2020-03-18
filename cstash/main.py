#!/usr/bin/env python3

import click
import os
from pathlib import Path

def entry_point():
    """
    An entry point for all calls. Needed because Click decorators do something odd
    with method calls, making the main() below only useful for CLI.
    """

    create_cstash_directory()
    main()

def create_cstash_directory():
    """ Ensure ~/.cstash directory exists and return it as a string """

    cstash_dir = "{}/.cstash".format(str(Path.home()))
    if not os.path.isdir(cstash_dir):
        os.mkdir(cstash_dir, mode=0o700)

    return cstash_dir

@click.group()
@click.option("--log-level", '-l', default="ERROR", type=click.Choice(["INFO", "ERROR", "DEBUG"]), help="How much information to show in logging. Default is ERROR")
@click.pass_context
def main(ctx=None, log_level=None, cstash_directory=create_cstash_directory()):
    ctx.obj = {'log_level': log_level, 'cstash_directory': cstash_directory}

from cstash.storage.commands import search as search_command
main.add_command(search_command)

from cstash.crypto.commands import stash as stash_command
main.add_command(stash_command)

if __name__ == "__main__":
    entry_point()
