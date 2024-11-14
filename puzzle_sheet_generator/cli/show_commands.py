import logging
from argparse import ArgumentParser, Namespace

from cliff.lister import Lister
from model.sheet_element import LichessPuzzle, PositionByFEN, SheetElement

from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.puzzle_store import PuzzleStore
from puzzle_sheet_generator.psg_cliff import PSGApp

puzzle_store_columns = ('StoreId', 'Name', 'nb puzzles', 'Themes', 'Openings', 'min_rating', 'max_rating')
puzzle_sheet_columns = ('SheetId', 'Name', 'nb puzzles')

class List(Lister):
    """List all available stores or sheets"""
    sheets_type_args = ('sh', 'sheet', 'sheets')
    store_type_args = ('st', 'store', 'stores')

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'list')
        self.log = logging.getLogger(__name__)
        self.app = app

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'type',
            choices = (*self.sheets_type_args, *self.store_type_args),
            help = 'Either "sh" for listing puzzle sheets or "st" for listing puzzle stores.'
        )
        return parser

    def take_action(self, parsed_args: Namespace) -> tuple[tuple, tuple]:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        if parsed_args.type in self.sheets_type_args:
            return self.show_sheets()
        if parsed_args.type in self.store_type_args:
            return self.show_stores()
        raise Exception(f'Unknown type {parsed_args.type} for {self.cmd_name} command.')

    def show_sheets(self) -> tuple[tuple, tuple]:
        data = (
            (
                sheet_id,
                sheet.get_name(),
                len(sheet)
            )
            for sheet_id, sheet in self.app.puzzle_sheet_repository.items.items()
        )
        return puzzle_sheet_columns, tuple(data)

    def show_stores(self) -> tuple[tuple, tuple]:
        data = (
            (
                store_id,
                store.get_name(),
                len(store),
                store.get_filtered_themes(),
                store.get_openings(),
                store.get_min_rating(),
                store.get_max_rating()
            )
            for store_id, store in self.app.puzzle_store_repository.items.items()
        )
        return puzzle_store_columns, tuple(data)


class Show(Lister):
    """Show details about a store or sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'show')
        self.log = logging.getLogger(__name__)
        self.app = app
        self.sheet_element_columns = (
        'PuzzleId',
        'FEN',
        'Moves',
        'Rating',
        'NbPlays',
        'Themes'
    )

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('name', help = 'Name or ID of the puzzle sheet or store to show.')
        return parser

    def take_action(self, parsed_args: Namespace) -> tuple[tuple, tuple]:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        store_id = self.app.puzzle_store_repository.get_id_for_name(parsed_args.name)
        sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.name)
        if store_id is not None:
            store = self.app.puzzle_store_repository.get_by_id(store_id)
            return self.show_store(store, store_id)
        elif sheet_id is not None:
            sheet = self.app.puzzle_sheet_repository.get_by_id(sheet_id)
            return self.show_sheet(sheet, sheet_id)
        else:
            self.log.error('The given name is unknown.')
        return (), ()

    def show_store(self, store: PuzzleStore, store_id: str) -> tuple[tuple, tuple]:
        store_data = (
            store_id,
            store.__len__(),
            store.get_filtered_themes(),
            store.get_openings(),
            store.get_min_rating(),
            store.get_max_rating()
        )
        return puzzle_store_columns, (store_data,)

    def show_sheet(self, sheet: PuzzleSheet, sheet_id: str) -> tuple[tuple, tuple]:
        self.log.info(f"Puzzle Sheet {sheet_id}:")
        data = (self.show_sheet_element(element) for element in sheet.elements)
        return self.sheet_element_columns, tuple(data)

    def show_sheet_element(self, sheet_element: SheetElement) -> tuple:
        match sheet_element:
            case LichessPuzzle():
                sheet_element: LichessPuzzle
                return (
                    sheet_element.puzzleId,
                    sheet_element.get_fen(),
                    sheet_element.get_number_of_moves(),
                    sheet_element.rating,
                    sheet_element.nb_plays,
                    sheet_element.themes
                )
            case PositionByFEN():
                return '', sheet_element.get_fen(), '', '', '', ''
            case _:
                raise Exception('Unexpected type of puzzle sheet element.')
