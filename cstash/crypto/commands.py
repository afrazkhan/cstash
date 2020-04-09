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
# FIXME: Either make --key non-optional, or default to getting the first private key in the chain
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.option('--force', '-f', is_flag=True, default=False, help='Force re-upload of already stored file')
@click.argument('filepath', metavar='filename')
@click.argument('bucket')
def stash(ctx, cryptographer, storage_provider, key, force, filepath, bucket):
    from cstash.crypto import crypto
    from cstash.crypto.filenames_database import FilenamesDatabase
    from cstash.storage.storage import Storage

    log_level = ctx.obj.get('log_level')
    logging.getLogger().setLevel(log_level)
    encryption = crypto.Encryption(ctx.obj.get('cstash_directory'), cryptographer, log_level)
    filename_db = FilenamesDatabase(ctx.obj.get('cstash_directory'), log_level)
    paths = helpers.get_paths(filepath)

    for this_path in paths:
        try:
            if filename_db.existing_hash(this_path) and force != True:
                print("This version of your file is already uploaded. Use -f to override and upload it again anyway")
                exit(0)
            if filename_db.existing_hash(this_path) and force == True:
                logging.warning("Re-uploaded same file: {}".format(this_path))

            filename_db_mapping = filename_db.store(this_path, cryptographer, storage_provider, bucket)
            logging.debug('Updated the local database with an entry for filename mapped to the obsfucated name')

            encrypted_file_path = encryption.encrypt(
                source_filepath=this_path, destination_filename=filename_db_mapping['entry'], key=key)
            logging.debug('Encrypted {} to {}'.format(this_path, filename_db_mapping['entry']))

            Storage(storage_provider, log_level=log_level).upload(bucket, encrypted_file_path)
            logging.debug('Uploaded {} to {}'.format(filename_db_mapping['entry'], storage_provider))

            logging.debug('Everything went fine, closing the DB connection')
            filename_db.close_db_connection(filename_db_mapping['db_connection'])
            print("File {} successfully uploaded".format(this_path))
            helpers.delete_file(encrypted_file_path)
        except Exception as e:
            logging.error("Couldn't encrypt/upload {}: {}".format(this_path, e))
            pass

@click.command()
@click.pass_context
@click.option('--storage-provider', '-s', type=click.Choice(['s3']), help='Override the object storage provider where the object is stored. Currently only the default option of S3 is supported.')
@click.option('--bucket', '-b', help='Override the known bucket for objects to be fetched')
@click.argument('original-filepath')
def fetch(ctx, storage_provider, bucket, original_filepath):
    from cstash.crypto import crypto
    from cstash.crypto.filenames_database import FilenamesDatabase
    from cstash.storage.storage import Storage

    log_level = ctx.obj.get('log_level')
    logging.getLogger().setLevel(log_level)
    cstash_directory = ctx.obj.get('cstash_directory')
    filename_db = FilenamesDatabase(cstash_directory, log_level)
    paths = helpers.get_paths(original_filepath)

    for this_path in paths:
        try:
            filename_db_mapping = filename_db.search(this_path, exact=True)

            file_hash = filename_db_mapping[0][1]['file_hash']
            cryptographer = filename_db_mapping[0][1]['cryptographer']
            storage_provider = storage_provider or filename_db_mapping[0][1]['storage_provider']
            bucket = filename_db_mapping[0][1]['bucket']
            logging.debug("Fetched {} {} from the database for {}".format(file_hash, cryptographer, original_filepath))

            temporary_file = "{}/{}".format(cstash_directory, file_hash)

            storage = Storage(storage_provider, log_level=log_level)
            storage.download(bucket, file_hash, temporary_file)
            logging.debug('Downloaded {} from {}'.format(file_hash, storage_provider))

            encryption = crypto.Encryption(
                cstash_directory=cstash_directory, cryptographer=cryptographer, log_level=log_level)
            encrypted_file_path = encryption.decrypt(temporary_file, this_path)
            logging.debug('Decrypted {} to {}'.format(filename_db_mapping[0][0], encrypted_file_path))
            helpers.delete_file(temporary_file)
        except Exception as e:
            logging.warning("Failed to decrypt {}: {}".format(this_path, e))
            pass
