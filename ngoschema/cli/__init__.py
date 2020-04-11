# -*- encoding: utf-8 -*
# from https://github.com/pallets/click/blob/master/examples/complex
import sys
import logging
import os
import click
import pathlib
import inflection
import traceback
from click.testing import CliRunner


class CliEnvironment(object):
    def __init__(self):
        self.verbose = False
        self.home = pathlib.Path.cwd()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)

    def resolve_path(self, path):
        return self.home.joinpath(path).resolve()


class ComplexCLI(click.MultiCommand):

    def __init__(self, module_name, cmd_folder, **kwargs):
        self.module_name = module_name
        self.cmd_folder = cmd_folder
        click.MultiCommand.__init__(self, **kwargs)

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(self.cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(inflection.dasherize(filename[4:-3]))
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode("ascii", "replace")
            mod = __import__(
                "{}.commands.cmd_{}".format(self.module_name, inflection.underscore(name)), None, None, ["cli"]
            )
        except ImportError as er:
            click.echo(er)
            return
        return mod.cli


pass_environment = click.make_pass_decorator(CliEnvironment, ensure=True)


@click.option(
    "-h", "--home",
    type=click.Path(exists=True, file_okay=False),
    help="Changes the folder to operate on.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option("-l", "--log-level", default='WARNING', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']),
              help="Set logging level")
@pass_environment
def base_cli(ctx, verbose, home, log_level):
    ctx.verbose = verbose
    if home:
        ctx.home = pathlib.Path(home)
    logging.getLogger().setLevel(getattr(logging, log_level))


def run_cli(command, args):
    runner = CliRunner()
    result = runner.invoke(command, args)
    if result.exit_code:
        er_msg = ''.join(traceback.format_exception(*result.exc_info))
        click.echo(er_msg, err=True)
    if result.stderr_bytes:
        click.echo(result.stderr, err=True)
    if result.stdout_bytes:
        click.echo(result.stdout, color='green')
