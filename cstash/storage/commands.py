import click
from cstash.libs import helpers
from cstash.libs.exceptions import CstashCriticalException
import logging

@click.group()
def storage():
    """ Perform operations on the backend storage """
    pass

@storage.command()
@click.pass_context
@click.option('--bucket', '-b', help='Bucket to search. Mandatory if you supply --filename')
@click.option('--filename', '-f', help='Filename to search for in --bucket')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only supports the default S3 provider')
def search(ctx, bucket=None, filename=None, storage_provider=None):
    """ Search the remote storage bucket for [filename] """

    from cstash.storage import storage

    if bucket == None and filename != None:
        raise CstashCriticalException(message="When searching for a file, you must specify a bucket")

    storage = storage.Storage(storage_provider, ctx.obj.get('log_level'))
    print(storage.search(bucket=bucket, filename=filename, storage_provider=storage_provider))
