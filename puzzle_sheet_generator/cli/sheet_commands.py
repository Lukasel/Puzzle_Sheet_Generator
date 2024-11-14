import contextlib
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

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

class Remove(Command):
    """Remove an element from a sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'remove')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

class Reorder(Command):
    """Reorder elements in a specific sheet"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'reorder')
        self.app = app
        self.log = logging.getLogger(__name__)

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        # todo

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
