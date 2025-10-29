import contextlib
import copy
import logging
import re
from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path

import chess
from cliff.command import Command

from puzzle_sheet_generator.cli.autosave_command import AutosaveCommand
from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.sheet_element import LichessPuzzle, PositionByFEN
from puzzle_sheet_generator.psg_cliff import PSGApp


class AddTo(AutosaveCommand):
    """Add an element to a specific sheet"""
    puzzle_id_regex = re.compile(r'^[A-Za-z0-9]{5,6}$')

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'add-to')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet.')
        parser.add_argument('puzzle', nargs='+', help = 'A Lichess puzzle id or a FEN string.')
        return parser

    def take_action(self, parsed_args) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        lichess_puzzle = None
        board = None
        puzzle = " ".join(parsed_args.puzzle).strip(" '\"")
        if self.puzzle_id_regex.match(puzzle):
            lichess_puzzle = self.app.puzzle_store_repository.get_main_store().get_puzzle_by_id(puzzle)
        else:
            with contextlib.suppress(ValueError):
                board = chess.Board(puzzle)
        if self._validate_args(parsed_args, sheet, lichess_puzzle, board):
            if lichess_puzzle is not None:
                sheet.add([lichess_puzzle])
            else:
                sheet.add([PositionByFEN(board)])
            self.log.info(f'The element was added to sheet "{sheet.get_name()}".')
            sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
            self.autosave_sheet(sheet, sheet_id)

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

class Remove(AutosaveCommand):
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
            index = parse_index(parsed_args.puzzle, sheet, self.log)
            if index is not None:
                sheet.remove_by_index(index)
                self.log.info(f'The element at index {index} was removed from sheet "{sheet.get_name()}".')
                sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
                self.autosave_sheet(sheet, sheet_id)

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        return True

class Reorder(AutosaveCommand):
    """Reorder elements in a specific sheet. Swaps the positions of two elements."""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'reorder')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet.')
        parser.add_argument('order', nargs=2, type=int, help = 'The puzzle_ids or indices of the elements to swap.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, sheet):
            index_1 = parse_index(parsed_args.order[0], sheet, self.log)
            index_2 = parse_index(parsed_args.order[1], sheet, self.log)
            sheet[index_1], sheet[index_2] = sheet[index_2], sheet[index_1]
            self.log.info(f'The elements at the indices {index_1} and {index_2} '
                          f'in sheet "{sheet.get_name()}" have been swapped.')
            sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
            self.autosave_sheet(sheet, sheet_id)

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

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help='Name or ID of the puzzle sheet.')
        parser.add_argument('name', help='New name of the puzzle sheet.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
        sheet = self.app.puzzle_sheet_repository.get_by_id(sheet_id)
        if self._validate_args(parsed_args, sheet):
            sheet.name = parsed_args.name
            self.log.info(f'Changed the name of the sheet with id "{sheet_id}" to "{sheet.get_name()}".')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        if self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.name) is not None:
            self.log.error(f'A puzzle sheet with the name or id "{parsed_args.name}" already exists.')
            return False
        return True

class Header(AutosaveCommand):
    """Specify what will be printed in the header above the puzzles"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'header')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help='Name or ID of the puzzle sheet.')
        parser.add_argument('-l', '--left-header', help='Text in the top left header')
        parser.add_argument('-r', '--right-header', help='Text in the top right header')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        if self._validate_args(parsed_args, sheet):
            if parsed_args.left_header is not None:
                sheet.left_header = parsed_args.left_header
            if parsed_args.right_header is not None:
                sheet.right_header = parsed_args.right_header
            self.log.info(f'The header of sheet "{sheet.get_name()}" has been set.')
            sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
            self.autosave_sheet(sheet, sheet_id)

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        return True

class Save(Command):
    """Save a sheet, so it can be reused across multiple sessions"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'save')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help='Name or ID of the puzzle sheet.')
        parser.add_argument('path', nargs='?', default='', help='Optional: Path to save the puzzle sheet at.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet_id = self.app.puzzle_sheet_repository.get_id_for_name(parsed_args.sheet)
        sheet = self.app.puzzle_sheet_repository.get_by_id(sheet_id)
        save_path = Path(parsed_args.path) if parsed_args.path != '' and not parsed_args.path.isspace() else None
        if self._validate_args(parsed_args, sheet, save_path):
            if save_path is None:
                self.app.save_file_service.save_sheet(sheet, sheet_id, self.app.config)
            else:
                self.app.save_file_service.save_to_path(sheet, save_path)
            self.log.info(f'Saved puzzle sheet "{sheet.get_name()}".')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet, save_path: Path | None) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
            return False
        if save_path is not None:
            if save_path.is_dir():
                self.log.error(f'The path "{parsed_args.path}" is a directory.')
                return False
            if save_path.exists():
                self.log.error(f'The file "{parsed_args.path}" already exists and would be overwritten.')
                return False
        return True

class Load(Command):
    """Load a saved sheet or a directory of saved sheets"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'load')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('path', nargs='?', default='', help='Optional: Path to load puzzle sheets from.')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        load_path = Path(parsed_args.path) if parsed_args.path != '' and not parsed_args.path.isspace() else None
        if self._validate_args(parsed_args, load_path):
            if load_path is None:
                puzzle_sheets = self.app.save_file_service.load(self.app.config)
            else:
                puzzle_sheets = self.app.save_file_service.load_from_path(load_path)
            sheet_ids = []
            for sheet in puzzle_sheets:
                sheet_ids.append(self.app.puzzle_sheet_repository.add(sheet))
            self.log.info(f'Loaded puzzle sheets with the ids {sheet_ids}.')

    def _validate_args(self, parsed_args: Namespace, load_path: Path | None) -> bool:
        if load_path is not None and not load_path.exists():
            self.log.error(f'The path "{parsed_args.path}" does not exist or is not readable.')
            return False
        return True

def parse_index(value: str, sheet: PuzzleSheet, log: Logger) -> int | None:
    index = sheet.find_index_by_puzzle_id(value)
    if index is None:
        with contextlib.suppress(Exception):
            index = int(value)
            if index < 0 or index >= len(sheet):
                log.error(f'"{value}" is neither a Lichess puzzle id '
                               f'nor a valid index in the sheet "{sheet.name}".')
    return index
