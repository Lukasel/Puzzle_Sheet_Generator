import sys

import puzzle_sheet_generator

from cliff.app import App
from cliff.commandmanager import CommandManager


class PSGApp(App):
    def __init__(self):
        super(PSGApp, self).__init__(
            puzzle_sheet_generator.__doc__.replace("\n", " ").strip(),
            puzzle_sheet_generator.__version__,
            CommandManager('puzzle_sheet_generator.cli'),
            deferred_help=True
        )

    def initialize_app(self, argv):
        # todo load config
        # config = load_config()
        # todo load lichess database
        # lichess_puzzle_db = LichessPuzzleDB(config)
        # todo initialize store and sheet container
        pass


    def clean_up(self, cmd, result, error):
        if error:
            self.LOG.error(f'An error occurred: {error}')


def main():
    myapp = PSGApp()
    return myapp.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
