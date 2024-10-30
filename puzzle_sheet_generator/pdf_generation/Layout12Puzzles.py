from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from puzzle_sheet_generator.pdf_generation.PuzzleLayout import PageSettings, PuzzleLayout


class Layout12Puzzles(PuzzleLayout):
    MAXIMUM_PUZZLES_IN_LAYOUT = 12

    def __init__(self, page_settings: PageSettings):
        super().__init__(page_settings)
        self.horizontal_skip = cm
        self.vertical_skip = 1.2 * cm
        self.header_to_content_margin = 0.8 * cm

    def place(self, svgs: list[tuple[str, bool]], page_canvas: canvas.Canvas) -> None:
        self.image_width = (self.page_settings.pagesize[0] - self.page_settings.margin_left_right() - 2 * self.horizontal_skip) / 3
        horizontal_image_spacing = self.image_width + self.horizontal_skip
        vertical_image_spacing = self.image_width + self.vertical_skip

        if len(svgs) > self.MAXIMUM_PUZZLES_IN_LAYOUT:
            svgs = svgs[:self.MAXIMUM_PUZZLES_IN_LAYOUT]

        for index, (svg, turn) in enumerate(svgs):
            x = self.page_settings.margin_left + (index % 3) * horizontal_image_spacing
            y = self.page_settings.pagesize[1] - self.page_settings.header_height - self.header_to_content_margin - (
                        (index // 3) % 4) * vertical_image_spacing
            self._place_puzzle(svg, turn, x, y, page_canvas)
