import logging

from cliff.command import Command

from puzzle_sheet_generator.psg_cliff import PSGApp


class AddTo(Command):
    """Add an element to a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'add-to')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Copy(Command):
    """Copy a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'copy')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Remove(Command):
    """Remove an element from a sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'remove')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Reorder(Command):
    """Reorder elements in a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'reorder')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Name(Command):
    """Change the name of a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'name')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Header(Command):
    """Specify what will be printed in the header above the puzzles"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'header')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Save(Command):
    """Save a sheet, so it can be reused across multiple sessions"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'save')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class Load(Command):
    """Load a saved sheet or a directory of saved sheets"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'load')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        # todo
