import click
from cstash.libs import helpers
import logging

helpers.set_logger()

# TODO: Declick the function below for re-use
# https://github.com/pallets/click/issues/40

@click.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported.')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported.')
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.argument('filename')
@click.argument('bucket')
def encrypt(ctx, cryptographer, storage_provider, key, filepath, bucket):
    from cstash.crypto import crypto
    encryption = crypto.Encryption(
        ctx.obj.get('cstash_directory'),
        cryptographer,
        key,
        ctx.obj.get('log_level'))

    paths = helpers.get_paths(filepath)

    from cstash.crypto.filenames import Filenames
    from cstash.storage.storage import Storage

    for f in paths:
        try:
            filename_db = Filenames(ctx.obj.get('cstash_directory'), ctx.obj.get('log_level'))
            filename_db_mapping = filename_db.store(filepath)
            logging.debug('Updated the local database with an entry for filename mapped to the obsfucated name')

            encrypted_file_path = encryption.encrypt(filepath=f, obsfucated_name=filename_db_mapping['entry'])
            logging.debug('Encrypted {} to {}'.format(filepath, f))

            Storage(storage_provider).upload(bucket, encrypted_file_path)
            logging.debug('Uploaded {} to {}'.format(filepath, storage_provider))

            logging.debug('Everything went fine, closing the DB connection')
            filename_db.close_db_connection(filename_db_mapping['db_connection'])
        except Exception as e:
            logging.error('Something went wrong: {}, rolling back the last entry from the DB'.format(e))
            # TODO: Do what the error message says
