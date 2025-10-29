import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from cliff.command import Command

from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.pdf_generation import generate_pdf
from puzzle_sheet_generator.pdf_generation.Layout6Puzzles import Layout6Puzzles
from puzzle_sheet_generator.pdf_generation.Layout12Puzzles import Layout12Puzzles
from puzzle_sheet_generator.pdf_generation.PuzzleLayout import HeaderFooterText, PageSettings, PuzzleLayout
from puzzle_sheet_generator.psg_cliff import PSGApp


class Print(Command):
    """Print a puzzle sheet to a PDF file"""

    def __init__(self, app: PSGApp, app_args):
        super().__init__(app, app_args, 'print')
        self.app = app
        self.log = logging.getLogger(__name__)

    def get_parser(self, prog_name) -> ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument('sheet', help = 'Name or ID of the puzzle sheet to print.')
        parser.add_argument(
            '-l', '--layout',
            choices = ('6', '12'),
            help = 'The layout of the generated PDF. '
                   'Either "6" or "12" for layouts with the respective number of puzzles on one page. If the layout is '
                   'not specified, a layout is chosen automatically to match the number of puzzles in the sheet.'
        )
        parser.add_argument('out_file', help = 'Filepath to where the generated PDF is saved.')
        parser.add_argument('--left-header', default = '', help = 'Text in the top left header')
        parser.add_argument('--right-header', default = '', help = 'Text in the top right header')
        parser.add_argument('--footer', default='', help = 'Text in the footer')
        return parser

    def take_action(self, parsed_args: Namespace) -> None:
        self.log.debug(f'Running {self.cmd_name} with arguments {parsed_args}')
        sheet = self.app.puzzle_sheet_repository.get(parsed_args.sheet)
        out_path = Path(parsed_args.out_file)
        if self._validate_args(parsed_args, sheet, out_path):
            if parsed_args.left_header != '' and not parsed_args.left_header.isspace():
                sheet.left_header = parsed_args.left_header
            if parsed_args.right_header != '' and not parsed_args.right_header.isspace():
                sheet.right_header = parsed_args.right_header
            if parsed_args.footer  != '' and not parsed_args.footer.isspace():
                sheet.footer = parsed_args.footer
            svgs = sheet.get_svgs(self.app.config)
            layout = self.get_layout(parsed_args)
            header_footer_text = HeaderFooterText(sheet.left_header, sheet.right_header, sheet.footer)
            generate_pdf.make_pdf_puzzle_page(out_path, svgs, header_footer_text, layout)
            self.log.info(f'Generated puzzle sheet "{sheet.get_name()}" at path {out_path}.')

    def _validate_args(self, parsed_args: Namespace, sheet: PuzzleSheet | None, out_path: Path) -> bool:
        if sheet is None:
            self.log.error(f'There is no sheet with name "{parsed_args.sheet}".')
        if out_path.exists() and out_path.is_file() and out_path.suffix.casefold() != '.pdf'.casefold():
            self.log.error(f'The path "{out_path}" is not a PDF file and would be overwritten. Print aborted.')
            return False
        return True

    def get_layout(self, parsed_args: Namespace) -> PuzzleLayout | None:
        if parsed_args.layout is None:
            return None
        page_settings = PageSettings()
        match parsed_args.layout:
            case '6':
                return Layout6Puzzles(page_settings)
            case '12':
                return Layout12Puzzles(page_settings)
            case _:
                raise Exception(f'Unknown page layout {parsed_args.layout} in {self.cmd_name} command.')
