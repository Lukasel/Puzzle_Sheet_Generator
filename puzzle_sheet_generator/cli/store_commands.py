import logging
from argparse import ArgumentParser, Namespace

from cliff.command import Command
from model.puzzle_sheet import PuzzleSheet
from model.puzzle_store import PuzzleStore
from model.repository import PuzzleStoreRepository
from pandas import DataFrame

from puzzle_sheet_generator.psg_cliff import PSGApp
from puzzle_sheet_generator.puzzle_database import lichess_puzzle_themes


class FilterArgs:
    """Parses and validates the filter command arguments"""
    def __init__(self, parsed_args: Namespace, puzzle_store_repository: PuzzleStoreRepository):
        self.log = logging.getLogger(__name__)
        self._valid = True

        self.store_name = parsed_args.store
        self.store_id = puzzle_store_repository.get_id_for_name(parsed_args.store)
        self.store = puzzle_store_repository.get_by_id(self.store_id)
        self.filtered_store_name = parsed_args.name

        self.filter_by_rating = parsed_args.min_rating is not None \
                                or parsed_args.max_rating is not None \
                                or parsed_args.rating is not None
        self.min_rating = parsed_args.rating - 100 if parsed_args.rating is not None else 0
        self.max_rating = parsed_args.rating + 100 if parsed_args.rating is not None else 10000
        if parsed_args.min_rating is not None:
            self.min_rating = parsed_args.min_rating
        if parsed_args.max_rating:
            self.max_rating = parsed_args.max_rating

        self.filter_by_themes = parsed_args.themes is not None
        self.themes_from_user = parsed_args.themes
        self.themes = lichess_puzzle_themes.to_canonical_forms(parsed_args.themes) \
            if parsed_args.themes is not None \
            else set()

        self.filter_by_opening_tags = parsed_args.openings is not None
        self.opening_tags = parsed_args.openings

        self.min_moves = 1
        self.max_moves = 1
        if parsed_args.moves is not None and (parsed_args.min_moves is not None or parsed_args.max_moves is not None):
            self.filter_by_moves = False
            self._valid = False
            self.log.error('The filtering argument "moves" cannot be used at the same time '
                           'with "--min-moves" or "--max_moves".')
        else:
            self.filter_by_moves = parsed_args.min_moves is not None \
                                   or parsed_args.max_moves is not None \
                                   or parsed_args.moves is not None
            if parsed_args.moves is not None:
                self.min_moves = parsed_args.moves
                self.max_moves = parsed_args.moves
            else:
                self.min_moves = parsed_args.min_moves if parsed_args.min_moves is not None else 1
                self.max_moves = parsed_args.max_moves if parsed_args.max_moves is not None else 1

        self._valid &= self.validate()

    def validate(self) -> bool:
        if self.store is None:
            self.log.error(f'There is no store with name "{self.store_name}".')
            return False
        if not self.filtered_store_name or self.filtered_store_name.isspace():
            self.log.error(f'The name "{self.filtered_store_name}" is not a valid name for a store.')
            return False
        if not self._validate_at_least_one_filter_active():
            return False
        valid = True
        valid &= self._validate_rating_args()
        valid &= self._validate_themes()
        valid &= self._validate_opening_tags()
        valid &= self._validate_move_args()
        return valid

    def _validate_at_least_one_filter_active(self) -> bool:
        if self.filter_by_rating is False \
                and self.filter_by_themes is False \
                and self.filter_by_opening_tags is False \
                and self.filter_by_moves is False:
            self.log.error('No filter was selected.')
            return False
        return True

    def _validate_rating_args(self) -> bool:
        if self.filter_by_rating and self.max_rating < self.min_rating:
            self.log.error('The maximum rating has to be greater or equal to the minimum rating.')
            self.log.warning('The "--rating" option sets "min-rating" to '
                                '"rating - 100" and "max-rating" to "rating + 100"')
            return False
        return True

    def _validate_themes(self) -> bool:
        if self.filter_by_themes is False:
            return True
        valid = True
        for theme in self.themes_from_user:
            # todo also allow german puzzle theme names
            if theme.casefold() not in lichess_puzzle_themes.casefold_puzzle_themes:
                self.log.error(f'The puzzle theme "{theme}" is not a lichess puzzle database theme.')
                # todo: suggest similar spelled themes
                valid = False
        return valid

    def _validate_opening_tags(self) -> bool:
        # todo: check opening tags
        return True

    def _validate_move_args(self) -> bool:
        if self.filter_by_moves is False:
            return True
        valid = True
        if self.min_moves < 1:
            self.log.error('The filtering argument "--moves" or "--min-moves" has to be at least "1".')
            valid = False
        if self.max_moves < 1:
            self.log.error('The filtering argument "--moves" or "--max-moves" has to be at least "1".')
            valid = False
        if self.max_moves < self.min_moves:
            self.log.error('The filtering argument "--max-moves" has to greater or equal to "--min-moves".')
            valid = False
        return valid

    def are_valid(self):
        return self._valid


class Filter(Command):
    """Create a store of puzzles by filtering from the db or an existing store"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'filter')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name: str) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('store', help='The puzzle store to filter puzzles from')
        parser.add_argument('name', help='Name for the new puzzle store')
        parser.add_argument('-t', '--themes', nargs='+', help='Filter by puzzle themes')
        parser.add_argument('-o', '--openings', nargs='+', help='Filter by opening tags')
        parser.add_argument('--min-moves', type=int, help='Filter for a minimum number of moves')
        parser.add_argument('--max-moves', type=int, help='Filter for a maximum number of moves')
        parser.add_argument('-m', '--moves', type=int, help='Filter for an exact number of moves')
        parser.add_argument('--min-rating', type=int, help='Filter for a minimum puzzle rating')
        parser.add_argument('--max-rating', type=int, help='Filter for a maximum puzzle rating')
        parser.add_argument(
            '-r', '--rating',
            type=int,
            help='Shorthand for setting "min-rating" to "rating - 100" and "max-rating" to "rating + 100"'
        )
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        filter_args = FilterArgs(parsed_args, self.app.puzzle_store_repository)
        if filter_args.are_valid():
            store = filter_args.store
            puzzle_dataframe = store.puzzle_df
            filtered_dataframe = self.filter_dataframe(puzzle_dataframe, filter_args)
            if filtered_dataframe.empty:
                self.log.error(f'The store "{store.name}" with id "{filter_args.store_id}" '
                              f'contains no puzzles that conform to the given filtering criteria.')
            else:
                filtered_themes = self.calc_filtered_themes(filter_args)
                filtered_opening_tags = {'mixed'}
                filtered_store = PuzzleStore(
                    filtered_dataframe,
                    filter_args.filtered_store_name,
                    filtered_themes,
                    filtered_opening_tags
                )
                filtered_store_id = self.app.puzzle_store_repository.add(filtered_store)
                self.log.info(f'Created new store "{parsed_args.name}" with id "{filtered_store_id}" '
                              f'that contains {len(filtered_dataframe.index)} puzzles.')

    @staticmethod
    def filter_dataframe(puzzle_dataframe: DataFrame, filter_args: FilterArgs) -> DataFrame:
        filtered_dataframe = puzzle_dataframe
        if filter_args.filter_by_rating:
            filtered_dataframe = PuzzleStore.filter_by_rating(
                filtered_dataframe,
                filter_args.min_rating,
                filter_args.max_rating
            )
        if filter_args.filter_by_themes:
            filtered_dataframe = PuzzleStore.filter_by_themes_all_match(
                filtered_dataframe,
                filter_args.themes
            )
        if filter_args.filter_by_opening_tags:
            filtered_dataframe = PuzzleStore.filter_by_opening_tags_any_match(
                filtered_dataframe,
                filter_args.opening_tags
            )
        if filter_args.filter_by_moves:
            filtered_dataframe = PuzzleStore.filter_by_moves(
                filtered_dataframe,
                filter_args.min_moves,
                filter_args.max_moves
            )
        return filtered_dataframe

    @staticmethod
    def calc_filtered_themes(filter_args: FilterArgs) -> set[str]:
        if filter_args.filter_by_themes is False:
            return filter_args.store.get_themes()
        else:
            return filter_args.store.get_themes().intersection(set(filter_args.themes))


class Sample(Command):
    """Create a new sheet or add to a sheet by sampling a given number of puzzles from a store"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'sample')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name: str) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('store', help='Name of the puzzle store to sample from')
        parser.add_argument('sheet', help='Name of the (possibly new) puzzle sheet to select puzzles for')
        parser.add_argument(
            '-a', '--amount', type=int,
            default=PuzzleSheet.MAX_AMOUNT_OF_PUZZLES,
            help='Number of puzzles to sample'
        )
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        store = self.app.puzzle_store_repository.get(parsed_args.store)
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, store, sheet):
            puzzles = store.sample(parsed_args.amount)
            if sheet is None:
                sheet = PuzzleSheet(parsed_args.sheet, puzzles)
                sheet_id = self.app.puzzle_sheet_repository.add(sheet)
                self.log.info(f'Created new sheet "{sheet.get_name()}" with id "{sheet_id}" '
                              f'that contains {len(sheet)} puzzles from store {store.get_name()}.')
            else:
                sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
                sheet.add(puzzles)
                self.log.info(f'Added {parsed_args.amount} puzzles to sheet "{sheet.get_name()}" with id "{sheet_id}".')

    def _validate_args(self, parsed_args: Namespace, store: PuzzleStore | None, sheet: PuzzleSheet | None) -> bool:
        if store is None:
            self.log.error(f'There is no store with name "{parsed_args.store_1}".')
        if parsed_args.amount <= 0:
            self.log.error('The selected amount of puzzles has to be positive.')
            return False
        max_amount = PuzzleSheet.MAX_AMOUNT_OF_PUZZLES \
            if sheet is None \
            else PuzzleSheet.MAX_AMOUNT_OF_PUZZLES - len(sheet)
        if max_amount == 0:
            self.log.error(f'There is no free space on puzzle sheet "{sheet.get_name()}".')
            return False
        if parsed_args.amount > max_amount:
            self.log.warning(f'The selected amount of {parsed_args.amount} puzzles, '
                             f'exceeds the free space on this sheet. Only {max_amount} puzzles are sampled.')
            parsed_args.amount = max_amount
        if parsed_args.amount > len(store):
            self.log.error(f'The selected puzzle store {store.get_name()} contains only {len(store)} puzzles.')
        return True


class Union(Command):
    """Unite two puzzle stores to create a mixed set of puzzles"""
    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'union')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name: str) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('store_1', help='A puzzle store selected for union')
        parser.add_argument('store_2', help='The other puzzle store selected for union')
        parser.add_argument('name', help='Name for the new puzzle store that combines the two selected stores puzzles')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        store_1 = self.app.puzzle_store_repository.get(parsed_args.store_1)
        store_2 = self.app.puzzle_store_repository.get(parsed_args.store_2)
        if self._validate_args(parsed_args, store_1, store_2):
            combined_store = store_1.combine(store_2, parsed_args.name)
            combined_store_id = self.app.puzzle_store_repository.add(combined_store)
            self.log.info(f'Created new store "{parsed_args.name}" with id "{combined_store_id}" '
                          f'that contains {len(combined_store.puzzle_df.index)} puzzles.')

    def _validate_args(self, parsed_args: Namespace, store_1: PuzzleStore | None, store_2: PuzzleStore | None) -> bool:
        """Return True if arguments are valid"""
        if store_1 is None or store_2 is None:
            self._log_missing_store_error(parsed_args, store_1, store_2)
            return False
        if not parsed_args.name or parsed_args.name.isspace():
            self.log.error(f'The name "{parsed_args.name}" is not a valid name for a store.')
            return False
        return True

    def _log_missing_store_error(
            self,
            parsed_args: Namespace, store_1: PuzzleStore | None,
            store_2: PuzzleStore | None
    ) -> None:
        if store_1 is None:
            self.log.error(f'There is no store with name "{parsed_args.store_1}".')
        if store_2 is None:
            self.log.error(f'There is no store with name "{parsed_args.store_2}".')
