from model.sheet_element import SheetElement


class PuzzleSheet:
    def __init__(self, elements: list[SheetElement] | None = None):
        self.elements = elements if elements is not None else []
