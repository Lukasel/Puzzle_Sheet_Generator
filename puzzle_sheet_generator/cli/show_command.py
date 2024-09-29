import logging

from cliff.lister import Lister

from model.puzzle_sheet import PuzzleSheet
from model.puzzle_store import PuzzleStore


class Show(Lister):
    """Show details about a store or sheet"""

    def __init__(self, app, app_args):
        super().__init__(app, app_args, 'show')
        self.log = logging.getLogger(__name__)
        # todo load column names dynamically from translation service
        self.puzzle_store_columns = ("id", "nb puzzles", "themes", "openings", "min_rating", "max_rating")
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
        # todo resolve name or id
        # todo show object
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
        return self.puzzle_store_columns, (store_data,)

    def show_sheet(self, sheet: PuzzleSheet, sheet_id: str) -> tuple:
        self.log.info(f"Puzzle Sheet {sheet_id}:")
        # todo
        data = ()
        return self.puzzle_sheet_columns, data
