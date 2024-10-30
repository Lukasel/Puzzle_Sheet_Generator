from pathlib import Path

import chess
import chess.svg

from puzzle_sheet_generator.configuration import config, diagram_board_colors
from puzzle_sheet_generator.pdf_generation.generate_pdf import make_pdf_puzzle_page
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db import LichessPuzzleDB

__all__ = ('make_svg', )


def make_svg(fen: str, moves: str) -> tuple[str, bool]:
    """
    Generate an SVG image of a chess position.
    :param fen: FEN string of the position
    :param moves: moves in the puzzle,
        applying the first move on the position from the FEN results in the puzzle position
    :return: Tuple of SVG string and side to move
    """
    board = chess.Board(fen)
    move_str = moves.split(' ')[0]
    move = chess.Move.from_uci(move_str)
    board.push(move)

    svg = chess.svg.board(
            board,
            orientation=board.turn,
            size=480,
            coordinates=True,
            colors=diagram_board_colors,
            borders=True,
        )

    out_path = Path('output', fen.replace('/', '_') + '.svg')
    with out_path.open('w') as f:
        f.write(svg)

    return (
        chess.svg.board(
            board,
            orientation=board.turn,
            size=480,
            coordinates=True,
            colors=diagram_board_colors,
            borders=True,
        ),
        board.turn
    )


if __name__ == '__main__':
    lichess_puzzle_db = LichessPuzzleDB(config['lichess_puzzle_db_path'])
    puzzles = lichess_puzzle_db.find_mate(2)
    puzzles = lichess_puzzle_db.filter_by_rating(puzzles.puzzle_df, 1250, 1400).sample(12)
    svgs = [make_svg(puzzle['FEN'], puzzle['Moves']) for _, puzzle in puzzles.iterrows()]
    make_pdf_puzzle_page('output/test.pdf', svgs, 'Matt', 'Matt in 2')
