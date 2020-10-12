"""
CLI commands for 'cstash config'
"""

import click

@click.group()
def config():
    """ Perform operations on the configuration file """
    pass # pylint: disable=unnecessary-pass

@config.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='python', type=click.Choice(['gpg', 'python']), help='The encryption service to use. Defaults to python')
@click.option('--storage-provider', '-s', default='s3', type=click.Choice(['s3']), help='The object storage provider to use. Currently only the default option of S3 is supported.')
@click.option('--s3-endpoint-url', '-e', default='https://s3.amazonaws.com', help='Used for other S3 compatible providers — e.g. https://ams3.digitaloceanspaces.com, defaults to https://s3.amazonaws.com')
@click.option('--ask-for-s3-credentials', '-a', is_flag=True, help="Prompt for access key ID and secret to be used with S3 compatible provider")
@click.option('--key', '-k', default='default', help='Key to use for encryption. For GPG, this is the key ID, for Python native encryption, this is the name of the file in the $HOME/.cstash/keys directory')
@click.option('--bucket', '-b', help='Bucket name where objects will be stored')
def write(ctx, cryptographer, storage_provider, s3_endpoint_url, ask_for_s3_credentials, key, bucket):
    """
    Set one or more of the options in the config file for [section]. If [section] is not
    given, default to "default". The config file will be created if necessary
    """

    from cstash.config.config import Config

    log_level = ctx.obj.get('log_level')

    s3_access_key_id = None
    s3_secret_access_key = None
    if ask_for_s3_credentials:
        print("Input will not be visible\n")
        s3_access_key_id = click.prompt("S3 Access Key", hide_input=True)
        s3_secret_access_key = click.prompt("S3 Secret Access Key", hide_input=True)

    config_class = Config(cstash_directory=ctx.obj.get('cstash_directory'), log_level=log_level)
    config_class.write(section=ctx.obj.get('profile'), options={
        "cryptographer": cryptographer,
        "storage_provider": storage_provider,
        "s3_endpoint_url": s3_endpoint_url,
        "s3_access_key_id": s3_access_key_id,
        "s3_secret_access_key": s3_secret_access_key,
        "key": key,
        "bucket": bucket})
