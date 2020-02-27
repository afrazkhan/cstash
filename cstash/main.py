#!/usr/bin/env python3

import click

@click.group()
@click.option("--log-level", '-l', default="INFO", type=click.Choice(["INFO", "ERROR", "DEBUG"]), help="How much information to show in logging. Default is INFO")
@click.pass_context
def main(ctx=None, log_level=None):
    ctx.obj = {'log_level': log_level}

from cstash.search.commands import search as search_command
main.add_command(search_command)

if __name__ == "__main__":
    main()
