import logging

from cliff.command import Command

from puzzle_sheet_generator.psg_cliff import PSGApp


class Filter(Command):
    """Create a store of puzzles by filtering from the db or an existing store"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'filter')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Sample(Command):
    """Create a new sheet or add to a sheet by sampling a given number of puzzles from a store"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'sample')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Union(Command):
    """Unite two puzzle stores to create a mixed set of puzzles"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'union')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo
