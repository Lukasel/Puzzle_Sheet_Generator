from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

import chess
import reportlab.lib.pagesizes as pagesizes
import svglib.svglib as svglib
from lxml import etree
from reportlab.graphics import renderPDF
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

__author__ = 'Lukas Malte Monnerjahn'
__all__ = 'make_pdf_puzzle_page, svg_to_rgl'

from puzzle_sheet_generator.pdf_generation.Layout12Puzzles import Layout12Puzzles
from puzzle_sheet_generator.pdf_generation.Layout6Puzzles import Layout6Puzzles


class PageSettings:
    def __init__(self):
        self.pagesize = pagesizes.A4
        self.margin_left = 1.5 * cm
        self.margin_right = 1.5 * cm
        self.font = 'Helvetica-Bold'
        self.font_size = 18
        self.header_height = 1.5 * cm + self.font_size

    def margin_left_right(self):
        return self.margin_left + self.margin_right


class PuzzleLayout(ABC):
    def __init__(self, page_settings: PageSettings):
        self.page_settings = page_settings
        self.vertical_skip = cm
        self.horizontal_skip = cm
        self.move_circle_radius = 0.18 * cm
        self.image_width = None

    @abstractmethod
    def place(self, svgs: List[Tuple[str, bool]], page_canvas: canvas.Canvas):
        pass

    def _place_puzzle(self, svg: str, turn: bool, x: float, y: float, page_canvas: canvas.Canvas):
        drawing = svg_to_rgl(svg)
        scaling_x = self.image_width / drawing.width
        scaling_y = self.image_width / drawing.height
        drawing.width = self.image_width
        drawing.height = self.image_width
        drawing.scale(scaling_x, scaling_y)
        renderPDF.draw(drawing, page_canvas, x, y - self.image_width)
        page_canvas.circle(x + self.image_width + 0.3 * cm, y - 0.1 * self.image_width, self.move_circle_radius, stroke=1,
                           fill=(turn == chess.BLACK))


def make_pdf_puzzle_page(outfile: str | Path, svgs: List[Tuple[str, bool]], theme: str, name: str):
    """
    Create a PDF file with up to 12 chess puzzles
    :param outfile: path to output
    :param svgs: list of tuples with SVG and side to move
    :param theme: general puzzle theme, printed left side in header
    :param name: more specific theme or name of the sheet or the author, printed right side in header
    """
    page_settings = PageSettings()
    puzzle_layout = Layout6Puzzles(page_settings) if len(svgs) <= 6 else Layout12Puzzles(page_settings)

    page_canvas = canvas.Canvas(
        str(outfile),
        pagesize=pagesizes.A4,
    )
    make_header(page_canvas, page_settings, theme, name)
    puzzle_layout.place(svgs, page_canvas)
    page_canvas.save()


def make_header(page_canvas: canvas.Canvas, page_settings: PageSettings, left_text: str, right_text: str):
    text_height = page_settings.pagesize[1] - cm - page_settings.font_size
    page_canvas.setFont(page_settings.font, page_settings.font_size)
    page_canvas.drawString(page_settings.pagesize[0] * 0.15, text_height, left_text)
    page_canvas.drawRightString(page_settings.pagesize[0] * 0.85, text_height, right_text)
    page_canvas.line(cm, page_settings.pagesize[1] - page_settings.header_height, page_settings.pagesize[0] - cm, page_settings.pagesize[1] - page_settings.header_height)


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
