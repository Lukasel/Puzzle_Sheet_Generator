from typing import TypeVar, Generic

from puzzle_sheet_generator.model.puzzle_sheet import PuzzleSheet
from puzzle_sheet_generator.model.puzzle_store import PuzzleStore

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

    def get_id_for_name(self, name: str) -> str | None:
        if name in self.items.keys():
            return name
        for item in self.items.values():
            if item.name == name:
                return item
        return None

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
        self.lichess_db_key = self.id_prefix + "0"

    def delete_by_id(self, id):
        if id == self.lichess_db_key:
            raise "Can't delete the Lichess Puzzle Database."
        del self.items[id]

    def reset_main_store(self, main_store: PuzzleStore):
        self.items[self.lichess_db_key] = main_store

class PuzzleSheetRepository(Repository[PuzzleSheet]):
    def __init__(self, id_prefix: str):
        super().__init__(id_prefix)