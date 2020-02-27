import click
from cstash.libs import helpers
import logging

helpers.set_logger()

@click.command()
@click.pass_context
@click.argument("bucket", required=False)
@click.argument("filename", required=False)
def search(ctx, bucket=None, filename=None):
    from cstash.search import s3

    s3 = s3.Search()
    print(s3.search(bucket=bucket, filename=filename))
