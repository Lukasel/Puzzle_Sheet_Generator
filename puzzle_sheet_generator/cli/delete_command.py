import logging

from cliff.command import Command

from psg_cliff import PSGApp


class Delete(Command):
    """Delete a sheet or store"""

    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'delete')
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('id')
        return parser

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        self.app.puzzle_store_repository.delete_by_id(parsed_args.id)
        self.app.puzzle_sheet_repository.delete_by_id(parsed_args.id)
