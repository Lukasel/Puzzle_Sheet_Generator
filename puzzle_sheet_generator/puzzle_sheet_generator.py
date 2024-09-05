from configuration import config, diagram_board_colors

import chess
import chess.svg

from puzzle_database.lichess_puzzle_db import LichessPuzzleDB
from pdf_generation.generate_pdf import make_pdf_puzzle_page

__author__ = 'Lukas Malte Monnerjahn'
__all__ = ('make_svg', 'make_pdf_puzzle_page')


def make_svg(fen: str, moves: str):
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

    with open('output/' + fen.replace('/', '_') + '.svg', 'w') as f:
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
    lichess_puzzle_db = LichessPuzzleDB(config)
    puzzles = lichess_puzzle_db.find_mate(2)
    puzzles = lichess_puzzle_db.filter_by_rating(puzzles, 1250, 1400).sample(12)
    svgs = [make_svg(puzzle['FEN'], puzzle['Moves']) for _, puzzle in puzzles.iterrows()]
    make_pdf_puzzle_page('output/test.pdf', svgs, "Matt", "Matt in 2")
