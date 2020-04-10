import click
from cstash.libs import helpers
from cstash.libs import exceptions as exceptions
import logging

@click.group()
def config():
    pass

@config.command()
@click.pass_context
@click.option('--section', '-n', default='default', type=click.Choice(['default']), help='The section of the configruation file to set. Defaults to "default"')
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported.')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported.')
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.option('--bucket', '-b', help='Override the known bucket for objects to be fetched')
def write(ctx, section, cryptographer, storage_provider, key, bucket):
    """
    Set one or more of the options in the config file for [section]. If [section] is not
    given, default to "default"
    """

    from cstash.config.config import Config

    log_level = ctx.obj.get('log_level')
    logging.getLogger().setLevel(log_level)

    config = Config(ctx.obj.get('cstash_directory'))
    config.write(section=section, options={
        "cryptographer": cryptographer,
        "storage_provider": storage_provider,
        "key": key,
        "bucket": bucket})
