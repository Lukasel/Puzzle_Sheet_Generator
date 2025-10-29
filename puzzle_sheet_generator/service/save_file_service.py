import json
from pathlib import Path

import chess
import platformdirs

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.sheet_element import LichessPuzzle, PositionByFEN, SheetElement
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db import LichessPuzzleDB


class SaveFileService:
    SHEETS_DIRECTORY = 'sheets'
    NAME_KEY = 'name'
    ELEMENTS_KEY = 'elements'
    LEFT_HEADER_KEY = 'left_header'
    RIGHT_HEADER_KEY = 'right_header'
    FOOTER_TEXT_KEY = 'footer_text'
    PUZZLE_ID_KEY = 'PuzzleId'
    FEN_KEY = 'FEN'
    JSON_FILE_TYPE = '.json'

    def __init__(self, lichess_puzzle_database: LichessPuzzleDB | None):
        self.lichess_puzzle_database = lichess_puzzle_database

    def save_sheet(self, puzzle_sheet: PuzzleSheet, sheet_id: str, app_config: AppConfig) -> None:
        data_path = platformdirs.user_data_path(app_config.app_name, ensure_exists=True) / self.SHEETS_DIRECTORY
        data_path.mkdir(exist_ok=True)
        file_name = sheet_id + self.JSON_FILE_TYPE
        self.save_to_path(puzzle_sheet, data_path / file_name)

    def save_to_path(self, puzzle_sheet: PuzzleSheet, save_path: Path) -> None:
        save_elements = [self._to_save_element(element) for element in puzzle_sheet.elements]
        save_data = {
            self.NAME_KEY: puzzle_sheet.name,
            self.ELEMENTS_KEY: save_elements,
            self.LEFT_HEADER_KEY: puzzle_sheet.left_header,
            self.RIGHT_HEADER_KEY: puzzle_sheet.right_header,
            self.FOOTER_TEXT_KEY: puzzle_sheet.footer,
        }
        with save_path.open('w') as save_file:
            json.dump(save_data, save_file, ensure_ascii=False)

    def _to_save_element(self, element: SheetElement) -> dict:
        match element:
            case LichessPuzzle():
                element: LichessPuzzle
                return {self.PUZZLE_ID_KEY: element.puzzleId, self.FEN_KEY: element.get_fen()}
            case PositionByFEN():
                return {self.FEN_KEY: element.get_fen()}
            case _:
                raise Exception(f'Unsupported type "{type(element)}" encountered while saving a puzzle sheet.')

    def load(self, app_config: AppConfig) -> list[PuzzleSheet]:
        data_path = platformdirs.user_data_path(app_config.app_name) / self.SHEETS_DIRECTORY
        return self.load_from_path(data_path)

    def load_from_path(self, load_path: Path) -> list[PuzzleSheet]:
        if not load_path.exists():
            raise Exception(f'The path "{load_path}" does not exist or is not readable.')
        if load_path.is_file():
            return [self._load_from_file(load_path)]
        if load_path.is_dir():
            loaded_sheets = []
            for fs_node in load_path.iterdir():
                if fs_node.is_file():
                    loaded_sheets.append(self._load_from_file(fs_node))
            return loaded_sheets
        else:
            raise Exception(f'The path "{load_path}" has an unexpected filetype.')

    def _load_from_file(self, load_file_path: Path) -> PuzzleSheet:
        with load_file_path.open('r') as load_file:
            data = json.load(load_file)
            name = data.get(self.NAME_KEY)
            elements_list = data.get(self.ELEMENTS_KEY)
            left_header = data.get(self.LEFT_HEADER_KEY)
            right_header = data.get(self.RIGHT_HEADER_KEY)
            if name is None or elements_list is None or left_header is None or right_header is None:
                raise Exception(f'The save file under "{load_file_path}" is missing required data.')
            footer = data.get(self.FOOTER_TEXT_KEY, '')
            elements = [self._from_save_element(save_element) for save_element in elements_list]
            elements = list(filter(lambda e: e is not None, elements))
            return PuzzleSheet(name, elements, left_header, right_header, footer)

    def _from_save_element(self, save_element: dict) -> SheetElement | None:
        puzzle_id = save_element.get(self.PUZZLE_ID_KEY)
        fen = save_element.get(self.FEN_KEY)
        if puzzle_id is not None and self.lichess_puzzle_database is not None:
            lichess_puzzle = self.lichess_puzzle_database.get_puzzle_by_id(puzzle_id)
            if lichess_puzzle is not None:
                return lichess_puzzle

        if fen is not None:
            return PositionByFEN(chess.Board(fen))

        return None
