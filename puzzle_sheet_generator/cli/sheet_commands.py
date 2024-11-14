import contextlib
import copy
import logging
import re
from argparse import ArgumentParser, Namespace

import chess
from cliff.command import Command

from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.sheet_element import LichessPuzzle, PositionByFEN
from puzzle_sheet_generator.psg_cliff import PSGApp


class AddTo(Command):
    """Add an element to a specific sheet"""
    puzzle_id_regex = re.compile(r'[A-Za-z0-9]{5,6}')

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'add-to')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet.')
        parser.add_argument('puzzle', help = 'A Lichess puzzle id or a FEN string.')
        return parser

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        lichess_puzzle = None
        board = None
        if self.puzzle_id_regex.match(parsed_args.puzzle):
            lichess_puzzle = self.app.puzzle_store_repository.get_main_store().get_puzzle_by_id(parsed_args.puzzle)
        else:
            with contextlib.suppress(ValueError):
                board = chess.Board(parsed_args.puzzle)
        if self._validate_args(parsed_args, sheet, lichess_puzzle, board):
            if lichess_puzzle is not None:
                sheet.add([lichess_puzzle])
            else:
                sheet.add([PositionByFEN(board)])
            self.log.info(f'The element was added to sheet "{sheet.get_name()}".')

    def _validate_args(
            self,
            parsed_args: Namespace,
            sheet: PuzzleSheet | None,
            puzzle: LichessPuzzle | None,
            board: chess.Board | None,
    ) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        if len(sheet) >= sheet.MAX_AMOUNT_OF_PUZZLES:
            self.log.error(f'There is no free space on puzzle sheet "{sheet.get_name()}".')
            return False
        if puzzle is None and board is None:
            self.log.error(f'"{parsed_args.puzzle}" is neither a Lichess puzzle id nor a FEN string.')
        return True

class Copy(Command):
    """Copy a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'copy')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet to copy.')
        parser.add_argument('new-sheet', help = 'Name for the new sheet.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, sheet):
            new_sheet = PuzzleSheet(
                parsed_args.new_sheet,
                copy.copy(sheet.elements),
                sheet.left_header,
                sheet.right_header
            )
            sheet_id = self.app.puzzle_sheet_repository.add(new_sheet)
            self.log.info(f'The puzzle sheet "{sheet.get_name()}" was copied to a new sheet with id "{sheet_id}".')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        if self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.new_sheet) is not None:
            self.log.error(f'A puzzle sheet with the name or id "{parsed_args.new_sheet}" already exists.')
            return False
        return True

class Remove(Command):
    """Remove an element from a sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'remove')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet.')
        parser.add_argument('puzzle', help = 'The Lichess puzzle id or the index of the element to remove.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, sheet):
            index = self.parse_index(parsed_args, sheet)
            if index is not None:
                sheet.remove_by_index(index)
                self.log.info(f'The element at index {index} was removed from sheet "{sheet.get_name()}".')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        return True

    def parse_index(self, parsed_args: Namespace, sheet: PuzzleSheet) -> int | None:
        index = sheet.find_index_by_puzzle_id(parsed_args.puzzle)
        if index is None:
            with contextlib.suppress(Exception):
                index = int(parsed_args.puzzle)
                if index < 0 or index >= len(sheet):
                    self.log.error(f'"{parsed_args.puzzle}" is neither a Lichess puzzle id '
                                   f'nor a valid index in the sheet "{sheet.name}".')
        return index

class Reorder(Command):
    """Reorder elements in a specific sheet. Swaps the positions of two elements."""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'reorder')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet.')
        parser.add_argument('order', nargs=2, type=int, help = 'The indices of the elements to swap.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, sheet):
            sheet[parsed_args.order[0]], sheet[parsed_args.order[1]] = (sheet[parsed_args.order[1]],
                                                                        sheet[parsed_args.order[0]])
            self.log.info(f'The elements at the indices {parsed_args.order[0]} and {parsed_args.order[1]} '
                          f'in sheet "{sheet.get_name()}" have been swapped.')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        for index in parsed_args.order:
            if index < 0 or index >= len(sheet):
                self.log.error(f'The sheet "{sheet.get_name()}" has only {len(sheet)} elements.')
                return False
        return True

class Name(Command):
    """Change the name of a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'name')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

class Header(Command):
    """Specify what will be printed in the header above the puzzles"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'header')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

class Save(Command):
    """Save a sheet, so it can be reused across multiple sessions"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'save')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

class Load(Command):
    """Load a saved sheet or a directory of saved sheets"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'load')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo
