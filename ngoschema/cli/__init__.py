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
        from .. import APP_CONTEXT
        self.verbose = False
        self.home = pathlib.Path.cwd()
        self.rc = APP_CONTEXT.create_child({})

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

    def load_context_file(self, fp, **opts):
        self.rc.load_default_context(fp, **opts)

    def repr(self, obj=None):
        obj = obj or self.obj
        if obj:
            click.echo('{')
            for k, v in obj.do_serialize().items():
                click.echo(f'\t{k}: {v}')
            click.echo('}')


class SpecialHelpMixin:
    banner = ''

    def format_help(self, ctx, formatter):
        if self.banner:
            formatter.write_paragraph()
            for line in self.banner.split('\n'):
                formatter.write_text(line)
        click.MultiCommand.format_help(self, ctx, formatter)
        repr_obj = getattr(ctx, 'obj', None)
        if repr_obj and not isinstance(repr_obj, CliEnvironment):
            ctx.repr(repr_obj)
            #formatter.write_text('{')
            #for k, v in repr_obj.do_serialize().items():
            #    formatter.write_text(f'\t{k}: {v}')
            #formatter.write_text('}')


class ComplexCLI(SpecialHelpMixin, click.MultiCommand):

    def __init__(self, module_name, cmd_folder, banner=None, **kwargs):
        from ngoschema import settings
        self.module_name = module_name
        self.cmd_folder = cmd_folder
        self.banner = banner or self.banner or settings.CLI_BANNER
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


class ComplexGroup(SpecialHelpMixin, click.Group):
    pass


pass_environment = click.make_pass_decorator(CliEnvironment, ensure=True)


@click.option(
    "-h", "--home",
    type=click.Path(exists=True, file_okay=False),
    help="Changes the folder to operate on.",
)
@click.option("-f", '--config-file', type=click.Path(), default=None, help='User configuration file')
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option("-l", "--log-level", default='WARNING', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']),
              help="Set logging level")
@pass_environment
def base_cli(ctx, home, config_file, verbose, log_level):
    ctx.verbose = verbose
    if home:
        ctx.home = pathlib.Path(home)
    from ngoschema import settings
    fn = ctx.rc.get('config_filename', settings.CLI_CONTEXT_FILENAME)
    config_file = ctx.resolve_path(config_file or fn)
    ctx.rc.load_default_context(config_file)
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
