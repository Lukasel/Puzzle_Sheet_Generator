from abc import ABC, abstractmethod

import chess
import chess.svg
from model.app_config import AppConfig


class SheetElement(ABC):
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    @abstractmethod
    def get_side_to_move(self) -> bool:
        pass

    @abstractmethod
    def get_svg(self) -> str:
        pass


class PositionByFEN(SheetElement):
    def __init__(self, fen: str, app_config: AppConfig):
        super().__init__(app_config)
        self.board = chess.Board(fen)

    def get_side_to_move(self) -> bool:
        return self.board.turn

    def get_svg(self) -> str:
        return svg_from_board(self.board, self.app_config.diagram_board_colors)


class Puzzle(SheetElement):
    def __init__(self, app_config: AppConfig):
        super().__init__(app_config)
        # todo
        self.board = chess.Board()

    def get_side_to_move(self) -> bool:
        return self.board.turn

    def get_svg(self) -> str:
        return svg_from_board(self.board, self.app_config.diagram_board_colors)


def svg_from_board(board: chess.Board, diagram_board_colors: dict[str, str]) -> str:
    return chess.svg.board(
            board,
            orientation=board.turn,
            size=480,
            coordinates=True,
            colors=diagram_board_colors,
            borders=True,
    )
