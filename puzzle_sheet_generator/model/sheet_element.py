from abc import ABC, abstractmethod
from collections import namedtuple

import chess
import chess.svg

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db_columns import lichess_puzzle_db_column_names

PuzzleTuple = namedtuple('PuzzleTuple', ' '.join(lichess_puzzle_db_column_names))


class SheetElement(ABC):
    def get_fen(self) -> str:
        return ''

    @abstractmethod
    def get_side_to_move(self) -> bool:
        pass

    @abstractmethod
    def get_svg(self, app_config: AppConfig) -> str:
        pass


class PositionByFEN(SheetElement):
    def __init__(self, board: chess.Board):
        super().__init__()
        self.board = board

    def get_fen(self) -> str:
        return self.board.fen()

    def get_side_to_move(self) -> bool:
        return self.board.turn

    def get_svg(self, app_config: AppConfig) -> str:
        return svg_from_board(self.board, app_config.diagram_board_colors)


class LichessPuzzle(SheetElement):
    def __init__(self, puzzle_tuple: PuzzleTuple):
        super().__init__()
        self.puzzleId = puzzle_tuple.PuzzleId

        self.board = chess.Board(puzzle_tuple.FEN)
        self.moves : str = puzzle_tuple.Moves

        # apply the first move, because the lichess puzzle db gives the FEN of the position before the puzzle
        first_move_uci_str = self.moves.split(' ')[0]
        first_move = chess.Move.from_uci(first_move_uci_str)
        self.board.push(first_move)

        self.rating = puzzle_tuple.Rating
        self.rating_deviation = puzzle_tuple.RatingDeviation
        self.popularity = puzzle_tuple.Popularity
        self.nb_plays = puzzle_tuple.NbPlays
        self.themes = puzzle_tuple.Themes
        self.game_url = puzzle_tuple.GameUrl
        self.opening_tags = puzzle_tuple.OpeningTags

    def get_fen(self) -> str:
        return self.board.fen()

    def get_number_of_moves(self) -> int:
        return (self.moves.count(' ') + 1) // 2

    def get_side_to_move(self) -> bool:
        return self.board.turn

    def get_svg(self, app_config: AppConfig) -> str:
        return svg_from_board(self.board, app_config.diagram_board_colors)


def svg_from_board(board: chess.Board, diagram_board_colors: dict[str, str]) -> str:
    return chess.svg.board(
            board,
            orientation=board.turn,
            size=480,
            coordinates=True,
            colors=diagram_board_colors,
            borders=True,
    )
