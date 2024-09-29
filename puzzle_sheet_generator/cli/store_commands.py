import logging

from cliff.command import Command

class Filter(Command):
    """Create a store of puzzles by filtering from the db or an existing store"""
    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'filter')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Sample(Command):
    """Create a new sheet or add to a sheet by sampling a given number of puzzles from a store"""

    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'sample')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Union(Command):
    """Unite two puzzle stores to create a mixed set of puzzles"""
    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'union')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        # todo