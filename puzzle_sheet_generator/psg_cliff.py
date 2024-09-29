import sys

import puzzle_sheet_generator

from cliff.app import App
from cliff.commandmanager import CommandManager

from model.repository import PuzzleSheetRepository, PuzzleStoreRepository
from service.translation_service import TranslationService


class PSGApp(App):
    def __init__(self):
        super(PSGApp, self).__init__(
            puzzle_sheet_generator.__doc__.replace("\n", " ").strip(),
            puzzle_sheet_generator.__version__,
            CommandManager('puzzle_sheet_generator.cli'),
            deferred_help=True
        )
        self.puzzle_store_repository = None
        self.puzzle_sheet_repository = None
        self.translation_service = None

    def initialize_app(self, argv):
        # todo load config
        # config = self.load_config()
        # todo load lichess database
        # lichess_puzzle_db = LichessPuzzleDB(config)
        # todo initialize store and sheet container
        # self.puzzle_store_repository = PuzzleStoreRepository("st", lichess_puzzle_db)
        self.puzzle_sheet_repository = PuzzleSheetRepository("sh")
        self.translation_service = TranslationService()
        pass


    def clean_up(self, cmd, result, error):
        if error:
            self.LOG.error(f'An error occurred: {error}')


def main():
    myapp = PSGApp()
    return myapp.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
