from typing import TypeVar, Generic

from model.puzzle_sheet import PuzzleSheet
from model.puzzle_store import PuzzleStore

T = TypeVar('T', type(PuzzleSheet), type(PuzzleStore))

class Repository(Generic[T]):
    def __init__(self, id_prefix: str, items: list[T] = None):
        if items is None:
            items = []
        self.counter = 0
        self.id_prefix = id_prefix
        self.items: dict[str, T] = {}
        for item in items:
            self.add(item)

    def add(self, item: T):
        self.items[self._next_id()] = item

    def _next_id(self):
        next_id = self.id_prefix + str(self.counter)
        self.counter += 1
        return next_id

    def get_by_id(self, id: str) -> T | None:
        return self.items.get(id)

    def get_by_name(self, name: str) -> T | None:
        for item in self.items.values():
            if item.name == name:
                return item
        return None

    def delete_by_id(self, id):
        del self.items[id]


class PuzzleStoreRepository(Repository[PuzzleStore]):
    def __init__(self, id_prefix: str, main_store: PuzzleStore):
        super().__init__(id_prefix, [main_store])

    def delete_by_id(self, id):
        if id == self.id_prefix + "0":
            raise "Can't delete the Lichess Puzzle Database."
        del self.items[id]


class PuzzleSheetRepository(Repository[PuzzleSheet]):
    def __init__(self, id_prefix: str):
        super().__init__(id_prefix)