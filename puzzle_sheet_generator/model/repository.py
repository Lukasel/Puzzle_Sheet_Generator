from typing import Generic, TypeVar

from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.puzzle_store import PuzzleStore

T = TypeVar('T', type(PuzzleSheet), type(PuzzleStore))

class Repository(Generic[T]):
    def __init__(self, id_prefix: str, items: list[T] | None = None):
        if items is None:
            items = []
        self.counter = 0
        self.id_prefix = id_prefix
        self.items: dict[str, T] = {}
        for item in items:
            self.add(item)

    def add(self, item: T) -> str:
        """Adds an element to the repository and returns its new id in the repository."""
        element_id = self._next_id()
        self.items[element_id] = item
        return element_id

    def _next_id(self) -> str:
        next_id = self.id_prefix + str(self.counter)
        self.counter += 1
        return next_id

    def get(self, id_or_name: str):
        element_id = self.get_id_for_name(id_or_name)
        return self.get_by_id(element_id)

    def get_id_for_name(self, name: str) -> str | None:
        if name in self.items:
            return name
        for element_id, element in self.items.items():
            if element.get_name() == name:
                return element_idbug
        return None

    def get_by_id(self, element_id: str) -> T | None:
        return self.items.get(element_id)

    def delete_by_id(self, element_id) -> None:
        del self.items[element_id]


class PuzzleStoreRepository(Repository[PuzzleStore]):
    def __init__(self, id_prefix: str, main_store: PuzzleStore):
        super().__init__(id_prefix, [main_store])
        self.lichess_db_key = self.id_prefix + "0"

    def delete_by_id(self, element_id) -> None:
        if element_id == self.lichess_db_key:
            raise Exception("Can't delete the Lichess Puzzle Database.")
        del self.items[element_id]

    def reset_main_store(self, main_store: PuzzleStore) -> None:
        self.items[self.lichess_db_key] = main_store

class PuzzleSheetRepository(Repository[PuzzleSheet]):
    def __init__(self, id_prefix: str):
        super().__init__(id_prefix)
