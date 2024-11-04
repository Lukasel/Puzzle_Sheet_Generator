import logging
from argparse import ArgumentParser, Namespace

from cliff.command import Command
from model.puzzle_store import PuzzleStore

from puzzle_sheet_generator.psg_cliff import PSGApp


class Filter(Command):
    """Create a store of puzzles by filtering from the db or an existing store"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'filter')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Sample(Command):
    """Create a new sheet or add to a sheet by sampling a given number of puzzles from a store"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'sample')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Union(Command):
    """Unite two puzzle stores to create a mixed set of puzzles"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'union')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('store_1')
        parser.add_argument('store_2')
        parser.add_argument('name')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        store_1 = self.app.puzzle_store_repository.get(parsed_args.store_1)
        store_2 = self.app.puzzle_store_repository.get(parsed_args.store_2)
        if self._validate_args(parsed_args, store_1, store_2):
            combined_store = store_1.combine(store_2, parsed_args.name)
            element_id = self.app.puzzle_store_repository.add(combined_store)
            self.log.info(f'Created new store "{parsed_args.name}" with id "{element_id}".')

    def _validate_args(self, parsed_args: Namespace, store_1: PuzzleStore | None, store_2: PuzzleStore | None) -> bool:
        """Return True if arguments are valid"""
        if store_1 is None or store_2 is None:
            self._log_missing_store_error(parsed_args, store_1, store_2)
            return False
        if not parsed_args.name or parsed_args.name.isspace():
            self.log.error(f'The name "{parsed_args.name}" is not a valid name for a store.')
            return False
        return True

    def _log_missing_store_error(
            self,
            parsed_args: Namespace, store_1: PuzzleStore | None,
            store_2: PuzzleStore | None
    ) -> None:
        if store_1 is None:
            self.log.error(f'There is no store with name "{parsed_args.store_1}".')
        if store_2 is None:
            self.log.error(f'There is no store with name "{parsed_args.store_2}".')
