import logging
from argparse import ArgumentParser, Namespace

from cliff.command import Command

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.psg_cliff import PSGApp


class ChangeConfig(Command):
    """Change the programs configuration"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'config')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('config_key', choices=AppConfig.CONFIG_KEYS)
        parser.add_argument('value')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        if parsed_args.config_key == AppConfig.LICHESS_PUZZLE_DB_KEY \
                and self.app.config.set(parsed_args.config_key, parsed_args.value):
            lichess_puzzle_db = self.app.load_lichess_puzzle_db()
            self.app.puzzle_store_repository.reset_main_store(lichess_puzzle_db)

        if parsed_args.config_key == AppConfig.DIAGRAM_BOARD_COLORS_PATH_KEY:
            self.app.config.set_diagram_board_colors_from_file(parsed_args.value)

        if parsed_args.config_key in AppConfig.BOOLEAN_CONFIGS:
            bool_value = self._parse_bool_value(parsed_args.value)
            if bool_value is None:
                self.log.warning(f'The given value {parsed_args.value} could not be parsed as boolean.')
            else:
                self.app.config.set(parsed_args.config_key, bool_value)

    true_values = ('true', 't', 'yes', 'y', 'wahr', 'w', 'ja', 'j')
    false_values = ('false', 'f', 'no', 'n', 'falsch', 'nein')
    def _parse_bool_value(self, value: str) -> bool | None:
        if str(value).lower() in self.true_values:
            return True
        if str(value).lower() in self.false_values:
            return False
        return None

class RestoreDefaultConfig(Command):
    """Restore the default configuration values"""
    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'config-default')
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name}')
        self.app.config.set_default_configuration()
