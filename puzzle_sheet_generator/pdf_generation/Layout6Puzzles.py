from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from puzzle_sheet_generator.pdf_generation.PuzzleLayout import PageSettings, PuzzleLayout


class Layout6Puzzles(PuzzleLayout):
    MAXIMUM_PUZZLES_IN_LAYOUT = 6

    def __init__(self, page_settings: PageSettings):
        super().__init__(page_settings)
        self.vertical_skip = 1.5 * cm
        self.horizontal_skip = 2 * cm
        self.move_circle_radius = 0.26 * cm
        self.header_to_content_margin = 0.8 * cm
        self.content_to_footer_margin = 0.5 * cm

    def place(self, svgs: list[tuple[str, bool]], page_canvas: canvas.Canvas) -> None:
        self.image_width = (self.page_settings.pagesize[1]
                            - self.page_settings.margin_header_footer()
                            - self.header_to_content_margin
                            - self.content_to_footer_margin
                            - 2 * self.horizontal_skip
                            ) / 3
        horizontal_image_spacing = self.image_width + self.horizontal_skip
        vertical_image_spacing = self.image_width + self.vertical_skip

        if len(svgs) > self.MAXIMUM_PUZZLES_IN_LAYOUT:
            svgs = svgs[:self.MAXIMUM_PUZZLES_IN_LAYOUT]

        for index, (svg, turn) in enumerate(svgs):
            x = self.page_settings.margin_left + (index % 2) * horizontal_image_spacing
            y = self.page_settings.pagesize[1] - self.page_settings.header_height - self.header_to_content_margin - (
                        (index // 2) % 3) * vertical_image_spacing
            self._place_puzzle(svg, turn, x, y, page_canvas)
