import logging

from cliff.command import Command

class Print(Command):
    """Change the programs configuration"""

    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'print')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        # todo
        self.log.info(f'Running {self.cmd_name}')
