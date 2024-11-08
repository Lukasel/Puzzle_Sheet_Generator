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
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet to print.')
        parser.add_argument(
            'layout',
            choices = ('6', '12'),
            help = 'The layout of the generated PDF. '
                   'Either "6" or "12" for layouts with the respective number of puzzles on one page.'
        )
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo
