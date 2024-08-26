__author__ = 'Lukas Malte Monnerjahn'

from typing import List, Tuple

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from puzzle_sheet_generator.pdf_generation.generate_pdf import PuzzleLayout, PageSettings


class Layout6Puzzles(PuzzleLayout):
    def __init__(self, page_settings: PageSettings):
        super().__init__(page_settings)
        self.vertical_skip = 1.5 * cm
        self.horizontal_skip = 1.5 * cm
        self.move_circle_radius = 0.26 * cm

    def place(self, svgs: List[Tuple[str, bool]], page_canvas: canvas.Canvas):
        self.image_width = (self.page_settings.pagesize[0] - self.page_settings.margin_left_right() - self.vertical_skip) / 2
        vertical_image_spacing = self.image_width + self.vertical_skip
        horizontal_image_spacing = self.image_width + self.horizontal_skip

        if len(svgs) > 6:
            svgs = svgs[:6]

        for index, (svg, turn) in enumerate(svgs):
            x = 1.5 * cm + (index % 2) * vertical_image_spacing
            y = self.page_settings.pagesize[1] - self.page_settings.header_height - cm - (
                        (index // 2) % 3) * horizontal_image_spacing
            self._place_puzzle(svg, turn, x, y, page_canvas)
