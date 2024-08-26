__author__ = 'Lukas Malte Monnerjahn'

from typing import List, Tuple

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from puzzle_sheet_generator.pdf_generation.PuzzleLayout import PuzzleLayout, PageSettings


class Layout12Puzzles(PuzzleLayout):
    def __init__(self, page_settings: PageSettings):
        super().__init__(page_settings)
        self.vertical_skip = cm
        self.horizontal_skip = 1.2 * cm

    def place(self, svgs: List[Tuple[str, bool]], page_canvas: canvas.Canvas):
        self.image_width = (self.page_settings.pagesize[0] - self.page_settings.margin_left_right() - 2 * self.vertical_skip) / 3
        vertical_image_spacing = self.image_width + cm
        horizontal_image_spacing = self.image_width + self.horizontal_skip

        if len(svgs) > 12:
            svgs = svgs[:12]

        for index, (svg, turn) in enumerate(svgs):
            x = 1.5 * cm + (index % 3) * vertical_image_spacing
            y = self.page_settings.pagesize[1] - self.page_settings.header_height - cm - (
                        (index // 3) % 4) * horizontal_image_spacing
            self._place_puzzle(svg, turn, x, y, page_canvas)
