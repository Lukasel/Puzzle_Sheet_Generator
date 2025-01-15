import abc
import logging

from cliff.command import Command

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet


class AutosaveCommand(Command, metaclass=abc.ABCMeta):
    def __init__(self, app, app_args, cmd_name: str):
        super().__init__(app, app_args, cmd_name)
        self.log = logging.getLogger(__name__)

    def autosave_sheet(self, sheet: PuzzleSheet, sheet_id: str):
        if self.app.config.get(AppConfig.AUTOSAVE_PUZZLE_SHEETS_KEY):
            self.app.save_file_service.save_sheet(sheet, sheet_id, self.app.config)
            self.log.debug(f'Autosaved sheet "{sheet_id}"')
