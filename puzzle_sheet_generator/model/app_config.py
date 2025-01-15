import json
import logging
from os import PathLike
from pathlib import Path

import platformdirs


class AppConfig:
    AUTOSAVE_PUZZLE_SHEETS_KEY = 'autosave_puzzle_sheets'
    DIAGRAM_BOARD_COLORS_PATH_KEY = 'diagram_board_colors_path'
    LICHESS_PUZZLE_DB_KEY = 'lichess_puzzle_db_path'

    BOOLEAN_CONFIGS = (AUTOSAVE_PUZZLE_SHEETS_KEY,)
    PATH_CONFIGS = (DIAGRAM_BOARD_COLORS_PATH_KEY, LICHESS_PUZZLE_DB_KEY)
    CONFIG_KEYS = BOOLEAN_CONFIGS + PATH_CONFIGS

    def __init__(self, app_name: str):
        self.log = logging.getLogger(__name__)
        self.app_name = app_name
        self.config = {}
        self.diagram_board_colors = None
        self.load_configuration()

    def get(self, key: str) -> bool | str:
        return self.config[key]

    def set(self, key: str, value: bool | str) -> bool:
        set_success = False
        if key in self.BOOLEAN_CONFIGS:
            set_success = self._set_boolean(key, value)
        if key in self.PATH_CONFIGS:
            set_success = self._set_path_config(key, value)
        if set_success:
            self.save_configuration()
        return set_success

    def _set_boolean(self, key: str, value) -> bool:
        if type(value) is bool:
            self.config[key] = value
            return True
        else:
            return False

    def _set_path_config(self, key: str, value) -> bool:
        path = Path(str(value))
        if not path.exists():
            self.log.warning(f'The given path {value} for configuration key {key} does not exist.')
            return False
        self.config[key] = str(value)
        return True

    def set_diagram_board_colors_from_file(self, board_colors_path: str | PathLike) -> None:
        if self.set(self.DIAGRAM_BOARD_COLORS_PATH_KEY, board_colors_path):
            self._set_diagram_board_colors()
        else:
            logging.warning(f'Could not load diagram board colors from "{board_colors_path}".')

    def _set_diagram_board_colors(self) -> None:
        try:
            with Path(self.config[self.DIAGRAM_BOARD_COLORS_PATH_KEY]).open('r') as file:
                self.diagram_board_colors = json.load(file)
        except OSError as error:
            self.log.error(f'Could not load diagram board colors '
                           f'from {self.config[self.DIAGRAM_BOARD_COLORS_PATH_KEY]}')
            self.log.error(error)

    def set_default_configuration(self) -> None:
        self.config = {
            self.AUTOSAVE_PUZZLE_SHEETS_KEY: True,
            self.DIAGRAM_BOARD_COLORS_PATH_KEY: 'config/diagram_board_colors.json'
        }
        self._set_diagram_board_colors()

    def set_default_configuration_including_lichess_db(self) -> None:
        self.set_default_configuration()
        self.config[self.LICHESS_PUZZLE_DB_KEY] = None

    def save_configuration(self) -> None:
        config_path = platformdirs.user_config_path(self.app_name, ensure_exists=True) / (self.app_name + '.conf')
        self.log.debug(f'Saving configuration to {config_path}')
        try:
            with config_path.open('w') as config_file:
                json.dump(self.config, config_file, ensure_ascii=False)
        except OSError as error:
            self.log.error(f'Could not save configuration to {config_path}.')
            self.log.error(error)

    def load_configuration(self) -> None:
        config_path = platformdirs.user_config_path(self.app_name) / (self.app_name + '.conf')
        self.log.debug(f'trying to load config form {config_path}')
        if config_path.exists() and config_path.is_file():
            self._load_configuration_from(config_path)
            self._set_diagram_board_colors()
        else:
            self.log.info('no configuration found, setting default values')
            self.set_default_configuration_including_lichess_db()
            self.save_configuration()

    def _load_configuration_from(self, config_path: Path) -> None:
        try:
            with config_path.open('r') as config_file:
                self.config = json.load(config_file)
        except OSError as error:
            self.log.error(f'Could not load configuration from {config_path}. Using default.')
            self.log.error(error)
            self.set_default_configuration()
