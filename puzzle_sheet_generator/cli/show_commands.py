import logging

from cliff.lister import Lister

from puzzle_sheet_generator.psg_cliff import PSGApp
from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.puzzle_store import PuzzleStore

# todo load column names dynamically from translation service
puzzle_store_columns = ("id", "nb puzzles", "themes", "openings", "min_rating", "max_rating")

class List(Lister):
    """List all available stores or sheets"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'list')
        self.log = logging.getLogger(__name__)
        self.app = app
        # todo load column names dynamically from translation service
        self.puzzle_sheet_columns = ('SheetId', 'Name', 'Header', 'nb puzzles')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('type', choices=['sh', 'sheets', 'st', 'stores'])
        return parser

    def take_action(self, parsed_args) -> tuple:
        self.log.debug(f'Running {self.cmd_name}')
        # todo
        return ()

    def show_sheets(self):
        # todo
        pass

    def show_stores(self):
        # todo
        pass


class Show(Lister):
    """Show details about a store or sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'show')
        self.log = logging.getLogger(__name__)
        self.app = app
        # todo load column names dynamically from translation service
        self.puzzle_sheet_columns = (
        'PuzzleId',
        'FEN',
        'Moves',
        'Rating',
        'RatingDeviation',
        'Popularity',
        'NbPlays',
        'Themes',
        'GameUrl',
        'OpeningTags'
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name')
        return parser

    def take_action(self, parsed_args) -> tuple:
        self.log.debug(f'Running {self.cmd_name} for name {parsed_args.name}')
        store_id = self.app.puzzle_store_repository.get_id_for_name(parsed_args.name)
        sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.name)
        if store_id is not None:
            store = self.app.puzzle_store_repository.get_by_id(store_id)
            self.show_store(store, store_id)
        elif sheet_id is not None:
            sheet = self.app.puzzle_sheet_repository.get_by_id(sheet_id)
            self.show_sheet(sheet, sheet_id)
        else:
            # todo Use translation service
            self.log.error('The given name is unknown.')
        return ()

    def show_store(self, store: PuzzleStore, store_id: str) -> tuple:
        store_data = (
            store_id,
            store.__len__(),
            store.get_themes(),
            store.get_openings(),
            store.get_min_rating(),
            store.get_max_rating()
        )
        return puzzle_store_columns, (store_data,)

    def show_sheet(self, sheet: PuzzleSheet, sheet_id: str) -> tuple:
        self.log.info(f"Puzzle Sheet {sheet_id}:")
        # todo
        data = ()
        return self.puzzle_sheet_columns, data
