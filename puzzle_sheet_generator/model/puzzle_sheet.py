from model.sheet_element import SheetElement


class PuzzleSheet:
    MAX_AMOUNT_OF_PUZZLES = 12

    def __init__(self, name: str, elements: list[SheetElement] | None = None):
        self.elements = elements if elements is not None else []
        self.name = name

    def get_name(self) -> str:
        return self.name

    def add(self, elements: list[SheetElement]):
        if len(self.elements) + len(elements) <= self.MAX_AMOUNT_OF_PUZZLES:
            self.elements += elements
        else:
            raise Exception(f'Too many puzzles ({len(elements)}) added to puzzle sheet {self.name} '
                            f'that already contains ({len(self.elements)}) elements '
                            f'(maximum {self.MAX_AMOUNT_OF_PUZZLES}).')

    def __len__(self):
        return len(self.elements)
