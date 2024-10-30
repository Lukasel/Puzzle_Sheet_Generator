import sys
from pathlib import Path

from cliff.app import App
from cliff.commandmanager import CommandManager

import puzzle_sheet_generator
from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.model.repository import PuzzleSheetRepository, PuzzleStoreRepository
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db import LichessPuzzleDB
from puzzle_sheet_generator.service.translation_service import TranslationService


class PSGApp(App):
    def __init__(self):
        super().__init__(
            puzzle_sheet_generator.__doc__.replace("\n", " ").strip(),
            puzzle_sheet_generator.__version__,
            CommandManager('puzzle_sheet_generator.cli'),
            deferred_help=True
        )
        self.app_name = 'puzzle_sheet_generator'
        self.config = AppConfig(self.app_name)
        self.puzzle_store_repository : PuzzleStoreRepository = None
        self.puzzle_sheet_repository : PuzzleSheetRepository = None
        self.translation_service = None

    def initialize_app(self, argv) -> None:
        self.translation_service = TranslationService()
        self.LOG.debug(f'initialising {self.app_name} app')
        lichess_puzzle_db = self.load_lichess_puzzle_db()
        self.puzzle_store_repository = PuzzleStoreRepository("st", lichess_puzzle_db)
        self.puzzle_sheet_repository = PuzzleSheetRepository("sh")

    def load_lichess_puzzle_db(self) -> LichessPuzzleDB | None:
        if self._check_lichess_puzzle_db_path():
            puzzle_db_path = self.config.get(AppConfig.LICHESS_PUZZLE_DB_KEY)
            self.LOG.info(f'Loading the Lichess Puzzle DB from {puzzle_db_path}. This may take a few seconds.')
            return LichessPuzzleDB(puzzle_db_path)
        else:
            # maybe todo let the app download the lichess puzzle db automatically
            return None

    def _check_lichess_puzzle_db_path(self) -> bool:
        lichess_puzzle_db_config = self.config.get(AppConfig.LICHESS_PUZZLE_DB_KEY)
        if lichess_puzzle_db_config is None:
            self.LOG.warning('The Lichess Puzzle Database is not configured.')
            return False
        lichess_puzzle_db_path = Path(lichess_puzzle_db_config)
        if not lichess_puzzle_db_path.exists():
            self.LOG.warning(f'The path to the Lichess Puzzle Database under {lichess_puzzle_db_path} does not exist.')
            return False
        if not lichess_puzzle_db_path.is_file():
            self.LOG.warning(f'The path to the Lichess Puzzle Database under {lichess_puzzle_db_path} is not a file.')
            return False
        if lichess_puzzle_db_path.suffix != ".csv":
            self.LOG.warning(f'The path to the Lichess Puzzle Database under {lichess_puzzle_db_path}'
                             f' does not have a CSV-file suffix (.csv).')
            return False
        return True

    def clean_up(self, cmd, result, error) -> None:
        if error:
            self.LOG.error(f'An error occurred: {error}')


def main():
    myapp = PSGApp()
    return myapp.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
