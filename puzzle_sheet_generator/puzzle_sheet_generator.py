from pathlib import Path
from typing import List, Tuple

import puzzle_sheet_generator.configuration as config

import chess
import chess.svg
import pandas
import reportlab.lib.pagesizes as pagesizes
import svglib.svglib as svglib
from lxml import etree
from reportlab.graphics import renderPDF
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

__author__ = 'Lukas Malte Monnerjahn'
__all__ = ('find_mate', 'find_themes', 'make_svg', 'make_pdf_puzzle_page')


column_names = (
    'PuzzleId',
    'FEN',
    'Moves',
    'Rating',
    'RatingDeviation',
    'Popularity',
    'NbPlays',
    'Themes',
    'GameUrl',
    'OpeningTags'
)

lichess_puzzles = pandas.read_csv(config.config["lichess_puzzle_db_path"], header=0, names=column_names)
# todo reduce startup time by having these precalculated
lichess_puzzles = lichess_puzzles[(lichess_puzzles['RatingDeviation'] <= 80)
                                  & (lichess_puzzles['Popularity'] >= 20)]
lichess_mate_puzzles = lichess_puzzles[lichess_puzzles['Themes'].str.contains('mate')]
lichess_no_mate_puzzles = lichess_puzzles[~lichess_puzzles['Themes'].str.contains('mate')]


def filter_by_rating(puzzles_df: pandas.DataFrame, min_rating: int, max_rating: int):
    return puzzles_df[(puzzles_df['Rating'] >= min_rating)
                      & (puzzles_df['Rating'] <= max_rating)]


def find_mate(moves: int):
    if moves == 1:
        return lichess_mate_puzzles[lichess_mate_puzzles['Themes'].str.contains('mateIn1')]
    if moves == 2:
        return lichess_mate_puzzles[lichess_mate_puzzles['Themes'].str.contains('mateIn2')]
    if moves == 3:
        return lichess_mate_puzzles[lichess_mate_puzzles['Themes'].str.contains('mateIn3')]
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
            colors=config.diagram_board_colors,
            borders=True,
        ),
        board.turn
    )


def svg_to_rgl(svg: str):
    """
    Transform an SVG to a ReportLab Graphics Drawing object
    :param svg: SVG string
    :return: ReportLab Graphics Drawing object
    """
    svg_root = etree.fromstring(svg)
    if svg_root is None:
        return
    svg_renderer = svglib.SvgRenderer("./fake.svg")
    return svg_renderer.render(svg_root)


def make_pdf_puzzle_page(outfile: str | Path, svgs: List[Tuple[str, bool]], theme: str, name: str):
    """
    Create a PDF file with up to 12 chess puzzles
    :param outfile: path to output
    :param svgs: list of tuples with SVG and side to move
    :param theme: general puzzle theme, printed left side in header
    :param name: more specific theme or name of the sheet or the author, printed right side in header
    """
    pagesize = pagesizes.A4
    font = 'Helvetica-Bold'
    font_size = 18
    header_height = 1.5 * cm + font_size

    def make_header(page_canvas: canvas.Canvas, left_text: str, right_text: str):
        text_height = pagesize[1] - cm - font_size
        page_canvas.setFont(font, font_size)
        page_canvas.drawString(pagesize[0] * 0.15, text_height, left_text)
        page_canvas.drawRightString(pagesize[0] * 0.85, text_height, right_text)
        page_canvas.line(cm, pagesize[1] - header_height, pagesize[0] - cm, pagesize[1] - header_height)

    def place_puzzles(page_canvas: canvas.Canvas, svgs):
        image_width = (pagesize[0] - 5 * cm) / 3
        vertical_image_spacing = image_width + cm
        horizontal_image_spacing = image_width + 1.2 * cm
        if len(svgs) > 12:
            svgs = svgs[:12]

        for index, (svg, turn) in enumerate(svgs):
            x = 1.5 * cm + (index % 3) * vertical_image_spacing
            y = pagesize[1] - header_height - cm - ((index // 3) % 4) * horizontal_image_spacing
            drawing = svg_to_rgl(svg)
            scaling_x = image_width / drawing.width
            scaling_y = image_width / drawing.height
            drawing.width = image_width
            drawing.height = image_width
            drawing.scale(scaling_x, scaling_y)
            renderPDF.draw(drawing, page_canvas, x, y - image_width)
            page_canvas.circle(x + image_width + 0.3 * cm, y - 0.1 * image_width, 0.18 * cm, stroke=1,
                               fill=(turn == chess.BLACK))

    page_canvas = canvas.Canvas(
        str(outfile),
        pagesize=pagesizes.A4,
    )
    make_header(page_canvas, theme, name)
    place_puzzles(page_canvas, svgs)
    page_canvas.save()


if __name__ == '__main__':
    puzzles = find_mate(2)
    puzzles = filter_by_rating(puzzles, 1250, 1400).sample(12)
    svgs = [make_svg(puzzle['FEN'], puzzle['Moves']) for _, puzzle in puzzles.iterrows()]
    make_pdf_puzzle_page('test.pdf', svgs, "Matt", "Matt in 2")
