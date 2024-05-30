# -*- encoding: utf-8 -*
# from https://github.com/pallets/click/blob/master/examples/complex
import sys
import logging
import os
import click
import pathlib
import inflection
import traceback
from click.core import Context
from click.testing import CliRunner

from ..utils.doc_rest_parser import parse_docstring


class CliEnvironment(object):

    def __init__(self, **opts):
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
        return self.rc.load_default_context(fp, **opts)

    def save_context_file(self, fp, **opts):
        self.rc.save_context_to_json(fp, **opts)

    def repr(self, key):
        obj = self.rc.get(key)
        if obj:
            click.echo(key + ' = {')
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
            formatter.write_text('{')
            for k, v in repr_obj.do_serialize().items():
                formatter.write_text(f'\t{k}: {v}')
            formatter.write_text('}')

    @staticmethod
    def format_docstring(docstring, arguments=False, returns=False):
        ds = parse_docstring(docstring)
        help = ds.get('description', '')
        if ds.get('longDescription'):
            help += f'\n\n{ds["longDescription"]}'
        if arguments and ds.get('arguments'):
            help += f'\n\nParameters: \n\n'
            for a in ds['arguments']:
                help += f'\t{a["name"]}'
                if a.get('description'):
                    help += f':\t{a["description"]}'
                help += f'\n\n'
        if returns and ds.get('returns'):
            returns = ds['returns']
            if returns.get('description'):
                help += f'\n\nReturns:\t{returns["description"]}'
        return help


class ComplexCLI(SpecialHelpMixin, click.MultiCommand):

    def __init__(self, module_name, cmd_folder=None, cmd_folders=[], banner=None, **kwargs):
        from ngoschema import settings
        self.module_name = module_name
        self.cmd_folders = cmd_folders or ([cmd_folder] if cmd_folder else [])
        self.banner = banner or self.banner or settings.CLI_BANNER
        click.MultiCommand.__init__(self, **kwargs)

    def list_commands(self, ctx):
        rv = []
        for cmd_folder in self.cmd_folders:
            for filename in os.listdir(cmd_folder):
                if filename.endswith(".py") and filename.startswith("cmd_"):
                    rv.append(inflection.dasherize(filename[4:-3]))
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode("ascii", "replace")
            cmd_name = f'cmd_{inflection.underscore(name)}'
            for cmd_folder in self.cmd_folders:
                cmd_file = f'{cmd_name}.py'
                if cmd_file in os.listdir(cmd_folder):
                    cmd_folder = pathlib.Path(cmd_folder)
                    path = cmd_folder.parts[cmd_folder.parts.index(self.module_name):]
                    mod = __import__(
                        "{}.cmd_{}".format('.'.join(path), inflection.underscore(name)), None, None, ["cli"]
                    )
                    break
            else:
                logging.error(f'{name} {self.cmd_folders}')
        except ImportError as er:
            logging.error(str(er))
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
    ctx.load_context_file(config_file)
    logging.getLogger().setLevel(getattr(logging, log_level))


def run_cli(command, args):
    runner = CliRunner()
    banner = getattr(command, 'banner', None)
    if banner:
        for b in banner.splitlines():
            if b.strip():
                click.echo(b)
    logging.getLogger().info('START %s' % command.name)
    result = runner.invoke(command, args)
    if result.exit_code:
        er_msg = ''.join(traceback.format_exception(*result.exc_info))
        click.echo(er_msg, err=True)
    if result.stderr_bytes:
        click.echo(result.stderr, err=True)
    if result.stdout_bytes:
        click.echo(result.stdout, color='green')
