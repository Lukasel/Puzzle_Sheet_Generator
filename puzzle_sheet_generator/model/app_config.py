import json
from os import PathLike
from pathlib import Path

import logging
import platformdirs


class AppConfig:
    AUTOSAVE_PUZZLE_SHEETS_KEY = 'autosave_puzzle_sheets'
    DIAGRAM_BOARD_COLORS_PATH_KEY = 'diagram_board_colors_path'
    LICHESS_PUZZLE_DB_KEY = 'lichess_puzzle_db_path'

    def __init__(self, app_name: str):
        self.log = logging.getLogger(__name__)
        self.app_name = app_name
        self.config = {}
        self.diagram_board_colors = None
        self.load_configuration()

    def get(self, key: str):
        return self.config[key]

    def set_diagram_board_colors_from_file(self, board_colors_path: str | PathLike):
        self.config[self.DIAGRAM_BOARD_COLORS_PATH_KEY] = board_colors_path
        self._set_diagram_board_colors()

    def _set_diagram_board_colors(self):
        try:
            with open(self.config[self.DIAGRAM_BOARD_COLORS_PATH_KEY]) as file:
                self.diagram_board_colors = json.load(file)
        except OSError as error:
            self.log.error(f'Could not load diagram board colors from {self.config[self.DIAGRAM_BOARD_COLORS_PATH_KEY]}')
            self.log.error(error)

    def set_default_configuration(self):
        self.config = {
            self.AUTOSAVE_PUZZLE_SHEETS_KEY: True,
            self.DIAGRAM_BOARD_COLORS_PATH_KEY: 'config/diagram_board_colors.json'
        }
        self._set_diagram_board_colors()

    def set_default_configuration_including_lichess_db(self):
        self.set_default_configuration()
        self.config[self.LICHESS_PUZZLE_DB_KEY] = None

    def save_configuration(self):
        config_path = platformdirs.user_config_path(self.app_name, ensure_exists=True) / (self.app_name + '.conf')
        self.log.info(f'Saving configuration to {config_path}')
        try:
            with open(config_path, 'w') as config_file:
                json.dump(self.config, config_file, ensure_ascii=False)
        except OSError as error:
            self.log.error(f'Could not save error to {config_path}.')
            self.log.error(error)

    def load_configuration(self):
        config_path = platformdirs.user_config_path(self.app_name) / (self.app_name + '.conf')
        self.log.info(f'trying to load config form {config_path}')
        if config_path.exists() and config_path.is_file():
            self.log.info('loading config from file')
            self._load_configuration_from(config_path)
        else:
            self.log.info('no config found, setting defaults')
            self.set_default_configuration_including_lichess_db()
            self.save_configuration()

    def _load_configuration_from(self, config_path: Path):
        try:
            with open(config_path, 'r') as config_file:
                self.config = json.load(config_file)
        except OSError as error:
            self.log.error(f'Could not load configuration from {config_path}. Using default.')
            self.log.error(error)
            self.set_default_configuration()
