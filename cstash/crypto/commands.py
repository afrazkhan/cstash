import click
from cstash.libs import helpers
import logging

helpers.set_logger()

@click.command()
@click.pass_context
@click.option('--cryptographer', '-c', default='gpg', type=click.Choice(['gpg']), help='The encryption service to use. Currently only the deault option of GnuPG is supported.')
def encrypt(ctx, cryptographer=None):
    from cstash.crypto import crypto
    crypto.Encryption(ctx.obj.get('cstash_directory'), cryptographer)
