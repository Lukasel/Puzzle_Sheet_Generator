from abc import ABC, abstractmethod

import chess
from lxml import etree
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from svglib import svglib


class PageSettings:
    def __init__(self):
        self.pagesize = pagesizes.A4
        self.margin_left = 1.5 * cm
        self.margin_right = 1.5 * cm
        self.margin_bottom = cm
        self.font = 'Helvetica-Bold'
        self.font_size = 18
        self.header_height = 1.5 * cm + self.font_size

    def margin_left_right(self) -> float:
        return self.margin_left + self.margin_right

    def margin_header_footer(self) -> float:
        return self.header_height + self.margin_bottom


class PuzzleLayout(ABC):
    def __init__(self, page_settings: PageSettings):
        self.page_settings = page_settings
        self.vertical_skip = cm
        self.horizontal_skip = cm
        self.move_circle_radius = 0.18 * cm
        self.image_width = None

    @abstractmethod
    def place(self, svgs: list[tuple[str, bool]], page_canvas: canvas.Canvas) -> None:
        pass

    def _place_puzzle(self, svg: str, turn: bool, x: float, y: float, page_canvas: canvas.Canvas) -> None:
        drawing = svg_to_rgl(svg)
        scaling_x = self.image_width / drawing.width
        scaling_y = self.image_width / drawing.height
        drawing.width = self.image_width
        drawing.height = self.image_width
        drawing.scale(scaling_x, scaling_y)
        renderPDF.draw(drawing, page_canvas, x, y - self.image_width)
        page_canvas.circle(
            x + self.image_width + self.move_circle_radius + 0.12 * cm,
            y - 0.1 * self.image_width,
            self.move_circle_radius,
            stroke=1,
            fill=(turn == chess.BLACK)
        )


def svg_to_rgl(svg: str) -> Drawing | None:
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
