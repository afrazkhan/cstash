import click

@click.group()
@click.pass_context
def daemon(ctx):
    """ Interact with the cstash daemon """

    from cstash.daemon.daemon import Daemon
    daemon_object = Daemon(ctx.obj.get('cstash_directory'), ctx.obj.get('log_level'), ctx)
    ctx.obj.update({'daemon': daemon_object})

@daemon.command()
@click.pass_context
def start(ctx):
    """ Start the daemon """

    ctx.obj.get('daemon').start()

@daemon.command()
@click.pass_context
def stop(ctx):
    """ Stop the daemon """

    ctx.obj.get('daemon').stop()
