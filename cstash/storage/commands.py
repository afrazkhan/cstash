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
@click.option('--s3-endpoint-url', '-e', help='Used for other S3 compatible providers — e.g. https://ams3.digitaloceanspaces.com')
def search(ctx, bucket=None, filename=None, storage_provider=None, s3_endpoint_url=None):
    """ Search the [bucket] on [storage_provider] for [filename] """

    from cstash.storage import storage as storage_module

    if bucket is None and filename is not None:
        raise CstashCriticalException(message="When searching for a file, you must specify a bucket")

    config = ctx.obj.get('config')
    s3_access_key_id = config['s3_access_key_id']
    s3_secret_access_key = config['s3_secret_access_key']

    storage_obj = storage_module.Storage(
        storage_provider=config["storage_provider"],
        log_level=ctx.obj.get('log_level'),
        s3_endpoint_url=config['s3_endpoint_url'],
        s3_access_key_id=config['s3_access_key_id'],
        s3_secret_access_key=config['s3_secret_access_key']
    )

    print(storage_obj.search(bucket=bucket, filename=filename, storage_provider=storage_provider))
