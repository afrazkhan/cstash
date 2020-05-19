"""
CLI methods for the storage command
"""

import click
from cstash.libs.exceptions import CstashCriticalException

@click.group()
def storage():
    """ Perform operations on the backend storage """
    pass # pylint: disable=unnecessary-pass

@storage.command()
@click.pass_context
@click.option('--bucket', '-b', help='Bucket to search. Mandatory if you supply --filename')
@click.option('--filename', '-f', help='Filename to search for in --bucket')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only supports the default S3 provider')
def search(ctx, bucket=None, filename=None, storage_provider=None):
    """ Search the [bucket] on [storage_provider] for [filename] """

    from cstash.storage import storage as storage_obj

    if bucket is None and filename is not None:
        raise CstashCriticalException(message="When searching for a file, you must specify a bucket")

    storage_obj = storage.Storage(storage_provider, ctx.obj.get('log_level'))
    print(storage.search(bucket=bucket, filename=filename, storage_provider=storage_provider))
