"""
CLI methods for the storage command
"""

import click
from cstash.libs.exceptions import CstashCriticalException
import cstash.libs.helpers as helpers

@click.group()
def storage():
    """ Perform operations on the backend storage """
    pass # pylint: disable=unnecessary-pass

@storage.command()
@click.pass_context
@click.option('--bucket', '-b', help='Bucket to search. Mandatory if you supply --filename')
@click.option('--filename', '-f', help='Filename to search for in --bucket')
@click.option('--s3-access-key-id', '-a', help='The S3 access key ID to authenticate with')
@click.option('--s3-secret-access-key', '-s', help='The S3 secret access key to authenticate with')
def search(ctx, bucket=None, filename=None, s3_access_key_id=None, s3_secret_access_key=None):
    """ Search the [bucket] on [storage_provider] for [filename] """

    from cstash.storage import storage as storage_module
    from cstash.crypto.filenames_database import FilenamesDatabase

    if bucket is None and filename is not None:
        raise CstashCriticalException(message="When searching for a file, you must specify a bucket")

    # Get what information we can from the local DB, instead of asking for it
    cstash_directory = ctx.obj.get('cstash_directory')
    filename_db = FilenamesDatabase(cstash_directory)

    paths = filename_db.search(filename)
    storage_providers = []
    for this_path in paths:
        storage_provider = this_path[1]['storage_provider']
        s3_endpoint_url = this_path[1]['s3_endpoint_url']
        bucket = this_path[1]['bucket']

        # Get what information we can from the config, instead of asking for it
        config = ctx.obj.get('config')
        config = helpers.merge_dicts(config, {
            "s3_access_key_id": s3_access_key_id,
            "s3_secret_access_key": s3_secret_access_key,
        })
        s3_access_key_id = config['s3_access_key_id']
        s3_secret_access_key = config['s3_secret_access_key']

        this_storage_provider = {
            'storage_provider': config["storage_provider"],
            's3_endpoint_url': s3_endpoint_url,
            's3_access_key_id': s3_access_key_id,
            's3_secret_access_key': s3_secret_access_key
        }
        if this_storage_provider not in storage_providers:
            storage_providers.append(this_storage_provider)

        # if s3_endpoint_url not in objects_by_endpoint.keys():
        #     objects_by_endpoint[s3_endpoint_url] = [ this_object ]
        # else:
        #     objects_by_endpoint[s3_endpoint_url].append(this_object)
        # for this_endpoint in objects_by_endpoint.values():
        #     storage_obj = storage_module.Storage(**this_endpoint[0])
        #     import pdb; pdb.set_trace()
                # print(storage_obj.search(bucket=bucket, filename=filename, storage_provider=storage_provider))

        # FIXME: This is incredibly inefficient. It creates a new Storage object for each file
        # (each iteration through this loop). It should instead group them by s3_endpoint_url,
        # and call Storage in that many batches

    for storage_provider in storage_providers:
        storage_obj = storage_module.Storage(**storage_provider)
        # FIXME: We're searching for the wrong thing here, filename != object. Need to decide
        #        what this command is going to actually do before fixing this; search for a real
        #        filename, or the obfuscated hash?
        print(storage_obj.search(bucket=bucket, filename=filename, storage_provider=storage_provider))
