import click
from cstash.libs import helpers
from cstash.libs import exceptions as exceptions
import logging

# TODO: Declick the functions below for re-use
# https://github.com/pallets/click/issues/40

@click.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported.')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported.')
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.argument('filepath', metavar='filename')
@click.argument('bucket')
def stash(ctx, cryptographer, storage_provider, key, filepath, bucket):
    log_level = ctx.obj.get('log_level')
    helpers.set_logger(level=log_level)
    from cstash.crypto import crypto
    encryption = crypto.Encryption(ctx.obj.get('cstash_directory'), cryptographer, log_level)

    paths = helpers.get_paths(filepath)

    from cstash.crypto.filenames import Filenames
    from cstash.storage.storage import Storage

    for f in paths:
        try:
            filename_db = Filenames(ctx.obj.get('cstash_directory'), log_level)
            filename_db_mapping = filename_db.store(f, cryptographer)
            logging.debug('Updated the local database with an entry for filename mapped to the obsfucated name')

            encrypted_file_path = encryption.encrypt(
                source_filepath=f, destination_filename=filename_db_mapping['entry'], key=key)
            logging.debug('Encrypted {} to {}'.format(f, filename_db_mapping['entry']))

            Storage(storage_provider, log_level=log_level).upload(bucket, encrypted_file_path)
            logging.debug('Uploaded {} to {}'.format(filename_db_mapping['entry'], storage_provider))

            logging.debug('Everything went fine, closing the DB connection')
            filename_db.close_db_connection(filename_db_mapping['db_connection'])
            # TODO: encryption.delete_temporary_file(obsfucated_name)
        except Exception as e:
            logging.error('Something went wrong: {}'.format(e))

@click.command()
@click.pass_context
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported.')
@click.argument('original-filepath')
@click.argument('bucket')
def fetch(ctx, storage_provider, original_filepath, bucket):
    log_level = ctx.obj.get('log_level')
    helpers.set_logger(level=log_level)

    from cstash.crypto import crypto
    from cstash.crypto.filenames import Filenames
    from cstash.storage.storage import Storage

    filename_db = Filenames(ctx.obj.get('cstash_directory'), log_level)
    filename_db_mapping = filename_db.search(original_filepath)
    if len(filename_db_mapping) == 0:
        raise exceptions.CstashCriticalException(message="Couldn't find {} in the database".format(original_filepath))

    obsfucated_name = filename_db_mapping[0][1]['obsfucated_name']
    cryptographer = filename_db_mapping[0][1]['cryptographer']
    logging.debug("Fetched {} {} from the database for {}".format(obsfucated_name, cryptographer, original_filepath))

    fetched_object = Storage(storage_provider, log_level=log_level).download(bucket, obsfucated_name, original_filepath)
    logging.debug('Downloaded {} from {}'.format(obsfucated_name, storage_provider))
    logging.error("Couldn't download {} from {}".format(obsfucated_name, storage_provider))

    encryption = crypto.Encryption(
        cstash_directory=ctx.obj.get('cstash_directory'), cryptographer=cryptographer, log_level=log_level)
    encrypted_file_path = encryption.decrypt(fetched_object, filename_db_mapping[0][0])
    logging.debug('Decrypted {} to {}'.format(filename_db_mapping[0][0], encrypted_file_path))
