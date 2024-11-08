from collections import namedtuple

from puzzle_sheet_generator.model.app_config import AppConfig
from puzzle_sheet_generator.model.sheet_element import SheetElement

SvgWithSideToMove = namedtuple('SvgWithSideToMove', 'svg side_to_move')


class PuzzleSheet:
    MAX_AMOUNT_OF_PUZZLES = 12

    def __init__(
            self,
            name: str,
            elements: list[SheetElement] | None = None,
            left_header: str = '',
            right_header: str = ''
    ):
        self.elements = elements if elements is not None else []
        self.name = name
        self.left_header = left_header
        self.right_header = right_header

    def get_name(self) -> str:
        return self.name

    def get_svgs(self, app_config: AppConfig) -> list[SvgWithSideToMove]:
        return [(element.get_svg(app_config), element.get_side_to_move()) for element in self.elements]

    def add(self, elements: list[SheetElement]):
        if len(self.elements) + len(elements) <= self.MAX_AMOUNT_OF_PUZZLES:
            self.elements += elements
        else:
            raise Exception(f'Too many puzzles ({len(elements)}) added to puzzle sheet {self.name} '
                            f'that already contains ({len(self.elements)}) elements '
                            f'(maximum {self.MAX_AMOUNT_OF_PUZZLES}).')

    def __len__(self):
        return len(self.elements)
