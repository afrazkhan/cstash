import click
from cstash.libs import helpers
from cstash.libs import exceptions as exceptions
import logging

# TODO: Declick the functions below for re-use
# https://github.com/pallets/click/issues/40

@click.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported')
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported')
@click.option('--bucket', '-b', help='Bucket to push objects to')
@click.option('--force', '-f', is_flag=True, default=False, help='Force re-upload of already stored file')
@click.argument('filepath', metavar='filename')
def stash(ctx, cryptographer, key, storage_provider, bucket, force, filepath):
    """ Encrypt, and upload objects to remote storage under hashed filenames """

    from cstash.crypto import crypto
    from cstash.crypto.filenames_database import FilenamesDatabase
    from cstash.storage.storage import Storage

    cstash_directory = ctx.obj.get('cstash_directory')

    # Override options retrieved from the config file, by those from the command line
    config = ctx.obj.get('config')
    helpers.merge_dicts(config, {
        "cryptographer": cryptographer,
        "storage_provider": storage_provider,
        "key": key,
        "bucket": bucket
    })

    log_level = ctx.obj.get('log_level')
    logging.getLogger().setLevel(log_level)
    encryption = crypto.Encryption(cstash_directory, config["cryptographer"], log_level)
    filename_db = FilenamesDatabase(cstash_directory, log_level)
    paths = helpers.get_paths(filepath)

    for this_path in paths:
        file_stored = filename_db.existing_hash(this_path)
        if file_stored and force != True:
            print("This version of your file is already uploaded. Use -f to override and upload it again anyway")
            exit(0)
        if file_stored and force == True:
            logging.warning("Re-uploading existing file: {}".format(this_path))

        filename_db_mapping = filename_db.store(this_path, config["cryptographer"], config["storage_provider"], config["bucket"])
        logging.debug('Updated the local database with an entry for filename mapped to the obsfucated name')

        encrypted_file_path = encryption.encrypt(
            source_filepath=this_path, destination_filename=filename_db_mapping['entry'], key=config["key"])
        logging.debug('Encrypted {} to {}'.format(this_path, filename_db_mapping['entry']))

        Storage(config["storage_provider"], log_level=log_level).upload(config["bucket"], encrypted_file_path)
        logging.debug('Uploaded {} to {}'.format(filename_db_mapping['entry'], config["storage_provider"]))

        logging.debug('Everything went fine, closing the DB connection')
        filename_db.close_db_connection(filename_db_mapping['db_connection'])
        print("File {} successfully uploaded".format(this_path))
        helpers.delete_file(encrypted_file_path)

@click.command()
@click.pass_context
@click.option('--storage-provider', '-s', type=click.Choice(['s3']), help='Override the object storage provider where the object is stored. Currently only the default option of S3 is supported.')
@click.option('--bucket', '-b', help='Override the known bucket for objects to be fetched')
@click.option('--ask-for-password', '-a', is_flag=True, help='Whether to ask for a password to decrypt the files with')
@click.argument('original-filepath')
def fetch(ctx, storage_provider, bucket, ask_for_password, original_filepath):
    """ Fetch encrypted files from remote storage and decrypt them """

    from cstash.crypto import crypto
    from cstash.crypto.filenames_database import FilenamesDatabase
    from cstash.storage.storage import Storage

    password = None
    if ask_for_password:
        password = click.prompt("Password", hide_input=True)

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
            encrypted_file_path = encryption.decrypt(temporary_file, this_path, password)
            logging.debug('Decrypted {} to {}'.format(filename_db_mapping[0][0], encrypted_file_path))
            helpers.delete_file(temporary_file)
        except Exception as e:
            logging.warning("Failed to decrypt {}: {}".format(this_path, e))
            pass

@click.group()
def database():
    """ Perform operations on the local database """
    pass

@database.command()
@click.pass_context
@click.argument('filename')
def search(ctx, filename):
    """ Search the local database for [filename]. Matches in any path will be returned """

    log_level = ctx.obj.get('log_level')

    from cstash.crypto.filenames_database import FilenamesDatabase

    filename_db = FilenamesDatabase(ctx.obj.get('cstash_directory'), log_level)
    results = filename_db.search(filename)
    if len(results) == 0:
        print("No results found")
    for r in results:
        print("Partial or full match: {}".format(r[0]))

@database.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported')
@click.option('--key', '-k', help='Key to use for encryption. For GPG, this is the key ID')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported')
@click.option('--bucket', '-b', help='Bucket to push objects to')
def backup(ctx, cryptographer, key, storage_provider, bucket):
    """ Encrypt and backup local database to remote storage """

    from cstash.crypto import crypto
    from cstash.storage.storage import Storage

    cstash_directory = ctx.obj.get('cstash_directory')

    # Override options retrieved from the config file, by those from the command line
    config = ctx.obj.get('config')
    helpers.merge_dicts(config, {
        "cryptographer": cryptographer,
        "storage_provider": storage_provider,
        "key": key,
        "bucket": bucket
    })

    log_level = ctx.obj.get('log_level')
    logging.getLogger().setLevel(log_level)
    encryption = crypto.Encryption(cstash_directory, config["cryptographer"], log_level)

    this_path = f"{cstash_directory}/filenames.sqlite"

    encrypted_file_path = encryption.encrypt(
        source_filepath=this_path, destination_filename="filenames.sqlite.encrypted", key=config["key"])
    logging.debug('Encrypted {} to {}'.format(this_path, f"{this_path}.encrypted"))

    Storage(config["storage_provider"], log_level=log_level).upload(config["bucket"], encrypted_file_path)
    logging.debug('Uploaded {} to {}'.format(f"{this_path}.encrypted", config["storage_provider"]))

    print("File {} successfully uploaded".format(this_path))
    helpers.delete_file(encrypted_file_path)
