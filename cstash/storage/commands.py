import click
from cstash.libs import helpers
from cstash.libs.exceptions import CstashCriticalException
import logging

helpers.set_logger()

@click.group()
def search():
    pass

@search.command()
@click.pass_context
@click.option('--bucket', '-b', help='Bucket to search. Mandatory if you supply --filename')
@click.option('--filename', '-f', help='Filename to search for in --bucket')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only supports the default S3 provider')
def remote(ctx, bucket=None, filename=None, storage_provider=None):
    """ Search the remote storage bucket for [filename] """

    from cstash.storage import storage

    if bucket == None and filename != None:
        raise CstashCriticalException(message="When searching for a file, you must specify a bucket")

    storage = storage.Storage(storage_provider, ctx.obj.get('log_level'))
    print(storage.search(bucket=bucket, filename=filename, storage_provider=storage_provider))

@search.command()
@click.pass_context
@click.argument('filename')
def local(ctx, filename):
    """ Search the local database for [filename]. Matches in any path will be returned """

    log_level = ctx.obj.get('log_level')

    from cstash.crypto.filenames import Filenames

    filename_db = Filenames(ctx.obj.get('cstash_directory'), log_level)
    results = filename_db.search(filename)
    if len(results) == 0:
        print("No results found")
    for r in results:
        print("Partial or full match: {}".format(r))
