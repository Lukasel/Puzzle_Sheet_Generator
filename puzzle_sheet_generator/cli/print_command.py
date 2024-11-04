import logging
from argparse import ArgumentParser, Namespace

from cliff.command import Command

from puzzle_sheet_generator.psg_cliff import PSGApp


class Print(Command):
    """Print a puzzle sheet to a PDF file"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'print')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo
