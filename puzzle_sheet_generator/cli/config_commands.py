import logging

from cliff.command import Command

class ChangeConfig(Command):
    """Change the programs configuration"""

    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'config')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        # todo

class RestoreDefaultConfig(Command):
    """Restore the default configuration values"""
    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'config-default')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug(f'Running {self.cmd_name}')
        # todo