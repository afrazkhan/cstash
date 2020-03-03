import click
from cstash.libs import helpers
import logging

helpers.set_logger()

@click.command()
@click.pass_context
@click.argument('bucket', required=False)
@click.argument('filename', required=False)
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only supports the default S3 provider.')
def search(ctx, bucket=None, filename=None, storage_provider=None):
    from cstash.storage import storage

    storage = storage.Search()
    print(storage.search(bucket=bucket, filename=filename, storage_provider=storage_provider))
