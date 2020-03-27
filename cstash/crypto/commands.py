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
@click.option('--force', '-f', is_flag=True, default=False, help='Force re-upload of already stored file')
@click.argument('filepath', metavar='filename')
@click.argument('bucket')
def stash(ctx, cryptographer, storage_provider, key, force, filepath, bucket):
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
            if filename_db.existing_hash(f) and force != True:
                print("This version of your file is already uploaded. Use -f to override and upload it again anyway")
                exit(0)
            if filename_db.existing_hash(f) and force == True:
                logging.warning("Re-uploaded same file: {}".format(f))

            filename_db_mapping = filename_db.store(f, cryptographer)
            logging.debug('Updated the local database with an entry for filename mapped to the obsfucated name')

            encrypted_file_path = encryption.encrypt(
                source_filepath=f, destination_filename=filename_db_mapping['entry'], key=key)
            logging.debug('Encrypted {} to {}'.format(f, filename_db_mapping['entry']))

            Storage(storage_provider, log_level=log_level).upload(bucket, encrypted_file_path)
            logging.debug('Uploaded {} to {}'.format(filename_db_mapping['entry'], storage_provider))

            logging.debug('Everything went fine, closing the DB connection')
            filename_db.close_db_connection(filename_db_mapping['db_connection'])
            print("File {} successfully uploaded".format(f))
            # TODO: helpers.delete_file(encrypted_file_path)
        except Exception as e:
            logging.error("Couldn't encrypt/upload {}: {}".format(f, e))

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

    cstash_directory = ctx.obj.get('cstash_directory')
    filename_db = Filenames(cstash_directory, log_level)
    filename_db_mapping = filename_db.search(original_filepath)
    if len(filename_db_mapping) == 0:
        raise exceptions.CstashCriticalException(message="Couldn't find {} in the database".format(original_filepath))

    file_hash = filename_db_mapping[0][1]['file_hash']
    cryptographer = filename_db_mapping[0][1]['cryptographer']
    logging.debug("Fetched {} {} from the database for {}".format(file_hash, cryptographer, original_filepath))

    temporary_file = "{}/{}".format(cstash_directory, file_hash)

    storage = Storage(storage_provider, log_level=log_level)
    fetched_object = storage.download(bucket, file_hash, temporary_file)
    logging.debug('Downloaded {} from {}'.format(file_hash, storage_provider))

    encryption = crypto.Encryption(
        cstash_directory=cstash_directory, cryptographer=cryptographer, log_level=log_level)
    encrypted_file_path = encryption.decrypt(temporary_file, original_filepath)
    logging.debug('Decrypted {} to {}'.format(filename_db_mapping[0][0], encrypted_file_path))
    # TODO: helpers.delete_file(temporary_file)
