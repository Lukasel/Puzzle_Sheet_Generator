import logging
from argparse import ArgumentParser, Namespace

from cliff.command import Command

from puzzle_sheet_generator.psg_cliff import PSGApp


class Delete(Command):
    """Delete a sheet or store"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'delete')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('name', help = 'Name or ID of the puzzle sheet or store to delete.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        self.app.puzzle_store_repository.delete_by_id(parsed_args.id)
        self.app.puzzle_sheet_repository.delete_by_id(parsed_args.id)
