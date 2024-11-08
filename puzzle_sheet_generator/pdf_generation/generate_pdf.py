from pathlib import Path

from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from puzzle_sheet_generator.pdf_generation.Layout6Puzzles import Layout6Puzzles
from puzzle_sheet_generator.pdf_generation.Layout12Puzzles import Layout12Puzzles
from puzzle_sheet_generator.pdf_generation.PuzzleLayout import PageSettings, PuzzleLayout

__all__ = ('make_pdf_puzzle_page',)

def make_pdf_puzzle_page(
        outfile: str | Path,
        svgs: list[tuple[str, bool]],
        theme: str,
        name: str,
        layout: PuzzleLayout | None = None
) -> None:
    """
    Create a PDF file with up to 12 chess puzzles
    :param outfile: path to output
    :param svgs: list of tuples with SVG and side to move
    :param theme: general puzzle theme, printed left side in header
    :param name: more specific theme or name of the sheet or the author, printed right side in header
    :param layout: a layout for the puzzles on the page
    """
    page_settings = PageSettings()
    puzzle_layout = layout
    if puzzle_layout is None:
        puzzle_layout = Layout6Puzzles(page_settings) \
            if len(svgs) <= Layout6Puzzles.MAXIMUM_PUZZLES_IN_LAYOUT \
            else Layout12Puzzles(page_settings)
    if type(layout) is Layout6Puzzles:
        page_settings.margin_left = 2 * cm
        page_settings.margin_right = 2 * cm

    page_canvas = canvas.Canvas(
        str(outfile),
        pagesize=pagesizes.A4,
    )
    make_header(page_canvas, page_settings, theme, name)
    puzzle_layout.place(svgs, page_canvas)
    page_canvas.save()


def make_header(page_canvas: canvas.Canvas, page_settings: PageSettings, left_text: str, right_text: str) -> None:
    text_height = page_settings.pagesize[1] - cm - page_settings.font_size
    page_canvas.setFont(page_settings.font, page_settings.font_size)
    page_canvas.drawString(page_settings.pagesize[0] * 0.15, text_height, left_text)
    page_canvas.drawRightString(page_settings.pagesize[0] * 0.85, text_height, right_text)
    page_canvas.line(
        cm,
        page_settings.pagesize[1] - page_settings.header_height,
        page_settings.pagesize[0] - cm,
        page_settings.pagesize[1] - page_settings.header_height
    )
