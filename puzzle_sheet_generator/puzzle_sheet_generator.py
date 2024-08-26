from typing import List

from configuration import config, diagram_board_colors

import chess
import chess.svg
import pandas

from lichess_puzzle_db import column_names
from pdf_generation.generate_pdf import make_pdf_puzzle_page

__author__ = 'Lukas Malte Monnerjahn'
__all__ = ('find_mate', 'find_themes', 'make_svg', 'make_pdf_puzzle_page')

lichess_puzzles = pandas.read_csv(config["lichess_puzzle_db_path"], header=0, names=column_names)
# todo reduce startup time by having these precalculated
lichess_puzzles = lichess_puzzles[(lichess_puzzles['RatingDeviation'] <= 80)
                                  & (lichess_puzzles['Popularity'] >= 20)]
lichess_mate_puzzles = lichess_puzzles[lichess_puzzles['Themes'].str.contains('mate')]
lichess_no_mate_puzzles = lichess_puzzles[~lichess_puzzles['Themes'].str.contains('mate')]


def filter_by_rating(puzzles_df: pandas.DataFrame, min_rating: int, max_rating: int):
    return puzzles_df[(puzzles_df['Rating'] >= min_rating)
                      & (puzzles_df['Rating'] <= max_rating)]


def find_mate(moves: int):
    if moves <= 5:
        return lichess_mate_puzzles[lichess_mate_puzzles['Themes'].str.contains(f'mateIn{moves}')]
    return lichess_mate_puzzles[(lichess_mate_puzzles['Moves'].count(' ') + 1) // 2 == moves]


def find_themes(themes: List[str], opening_tag: str | None):
    def find_theme(puzzles_df: pandas.DataFrame, theme: str):
        return puzzles_df[puzzles_df['Themes'].str.contains(theme)]

    def find_opening(puzzles_df: pandas.DataFrame, opening_tag: str):
        return puzzles_df[puzzles_df['OpeningTags'].str.contains(opening_tag)]

    for theme in themes:
        lichess_no_mate_puzzles = find_theme(lichess_no_mate_puzzles, theme)
    if opening_tag:
        lichess_no_mate_puzzles = find_opening(lichess_no_mate_puzzles, opening_tag)
    return lichess_no_mate_puzzles


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
    puzzles = find_mate(2)
    puzzles = filter_by_rating(puzzles, 1250, 1400).sample(12)
    svgs = [make_svg(puzzle['FEN'], puzzle['Moves']) for _, puzzle in puzzles.iterrows()]
    make_pdf_puzzle_page('output/test.pdf', svgs, "Matt", "Matt in 2")
