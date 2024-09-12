import logging

from cliff.command import Command

class ConfigCommand(Command):
    """Change the programs configuration"""
    cmd_name = 'config'

    def __init__(self, app, app_args):
        super().__init__(app, app_args, self.cmd_name)
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        # todo
        self.log.info(f'Running {self.cmd_name}')
