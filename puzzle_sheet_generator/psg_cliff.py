import sys
from pathlib import Path

import puzzle_sheet_generator

from cliff.app import App
from cliff.commandmanager import CommandManager

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.model.repository import PuzzleSheetRepository, PuzzleStoreRepository
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db import LichessPuzzleDB
from puzzle_sheet_generator.service.translation_service import TranslationService


class PSGApp(App):
    def __init__(self):
        super(PSGApp, self).__init__(
            puzzle_sheet_generator.__doc__.replace("\n", " ").strip(),
            puzzle_sheet_generator.__version__,
            CommandManager('puzzle_sheet_generator.cli'),
            deferred_help=True
        )
        self.app_name = 'puzzle_sheet_generator'
        self.config = None
        self.puzzle_store_repository = None
        self.puzzle_sheet_repository = None
        self.translation_service = None

    def initialize_app(self, argv):
        self.translation_service = TranslationService()
        self.LOG.info('initialising app')
        self.config = AppConfig(self.app_name)
        if self.config.get(AppConfig.LICHESS_PUZZLE_DB_KEY):
            lichess_db_path = Path(self.config.get(AppConfig.LICHESS_PUZZLE_DB_KEY))
            if lichess_db_path.exists() and lichess_db_path.is_file():
                self._initialize_repositories()
            else:
                self.LOG.warning('The Lichess Puzzle Database is not configured.')
        else:
            self.LOG.warning('The Lichess Puzzle Database is not configured.')

    def _initialize_repositories(self):
        lichess_puzzle_db = LichessPuzzleDB(self.config.get(AppConfig.LICHESS_PUZZLE_DB_KEY))
        self.puzzle_store_repository = PuzzleStoreRepository("st", lichess_puzzle_db)
        self.puzzle_sheet_repository = PuzzleSheetRepository("sh")


    def clean_up(self, cmd, result, error):
        if error:
            self.LOG.error(f'An error occurred: {error}')


def main():
    myapp = PSGApp()
    return myapp.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
