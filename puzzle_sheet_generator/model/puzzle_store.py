from collections.abc import Collection
from numbers import Number
from typing import Self

import pandas

from puzzle_sheet_generator.model.sheet_element import LichessPuzzle
from puzzle_sheet_generator.puzzle_database import lichess_puzzle_themes


class PuzzleStore:
    max_themes_for_display = 4

    def __init__(
            self,
            puzzle_df: pandas.DataFrame,
            name: str,
            themes: set[str] | None = None,
            opening_tags: set[str] | None = None
    ):
        self.puzzle_df = puzzle_df
        self.name = name
        self._themes = themes if themes is not None else lichess_puzzle_themes.all_puzzle_themes
        self._opening_tags = opening_tags if opening_tags is not None else {'mixed'}

    def __len__(self) -> int:
        return self.puzzle_df.__len__()

    def combine(self, other_store: Self, name: str) -> Self:
        """Create a new puzzle store, that combines this and the other puzzle stores puzzles into one store."""
        combined_df = self.puzzle_df.combine_first(other_store.puzzle_df)
        combined_opening_tags = self.combine_tags(self._opening_tags, other_store.opening_tags)
        return PuzzleStore(
            combined_df,
            name,
            self._themes.union(other_store._themes),
            combined_opening_tags
        )

    def get_name(self) -> str:
        return self.name

    def get_themes(self) -> set[str]:
        return self._themes

    def get_filtered_themes(self) -> set[str]:
        return self._themes if self.max_themes_for_display >= len(self._themes) > 0 else {'mixed'}

    def get_openings(self) -> set[str]:
        return self._opening_tags

    def get_min_rating(self) -> int:
        return self.puzzle_df['Rating'].min()

    def get_max_rating(self) -> int:
        return self.puzzle_df['Rating'].max()

    def get_median_rating(self) -> Number:
        return self.puzzle_df['Rating'].median()

    def get_puzzle_by_id(self, puzzle_id: str) -> LichessPuzzle | None:
        puzzle_data = self.puzzle_df[self.puzzle_df['PuzzleId'] == puzzle_id]
        if puzzle_data is not None and not puzzle_data.empty:
            assert len(puzzle_data.index) == 1
            return LichessPuzzle(next(puzzle_data.itertuples(index=False)))
        else:
            return None

    def sample(self, amount: int) -> list[LichessPuzzle]:
        puzzle_sample = []
        for puzzle in self.puzzle_df.sample(amount).itertuples(index=False):
            puzzle_sample.append(LichessPuzzle(puzzle))
        return puzzle_sample

    @staticmethod
    def filter_by_rating(puzzles_df: pandas.DataFrame, min_rating: int, max_rating: int) -> pandas.DataFrame:
        return puzzles_df[(puzzles_df['Rating'] >= min_rating)
                          & (puzzles_df['Rating'] <= max_rating)]

    @staticmethod
    def filter_by_moves(puzzles_df: pandas.DataFrame, min_moves: int, max_moves: int) -> pandas.DataFrame:
        return puzzles_df[((puzzles_df['Moves'].str.count(' ') + 1) // 2 >= min_moves)
                          & ((puzzles_df['Moves'].str.count(' ') + 1) // 2 <= max_moves)]

    @staticmethod
    def filter_by_themes_any_match(puzzles_df: pandas.DataFrame, themes: Collection[str]) -> pandas.DataFrame:
        regex_pattern = PuzzleStore.build_regex_pattern(themes)
        return puzzles_df[puzzles_df['Themes'].str.contains(regex_pattern)]

    @staticmethod
    def filter_by_themes_all_match(puzzles_df: pandas.DataFrame, themes: Collection[str]) -> pandas.DataFrame:
        regex_pattern = PuzzleStore.build_regex_pattern(themes)
        expected_matches = len(themes)
        return puzzles_df[puzzles_df['Themes'].str.count(regex_pattern) == expected_matches]

    @staticmethod
    def filter_by_themes_none_match(puzzles_df: pandas.DataFrame, themes: Collection[str]) -> pandas.DataFrame:
        regex_pattern = PuzzleStore.build_none_match_regex_pattern(themes)
        return puzzles_df[puzzles_df['Themes'].str.match(regex_pattern)]

    @staticmethod
    def filter_by_opening_tags_any_match(
            puzzles_df: pandas.DataFrame,
            opening_tags: Collection[str]
    ) -> pandas.DataFrame:
        regex_pattern = PuzzleStore.build_regex_pattern(opening_tags)
        return puzzles_df[puzzles_df['OpeningTags'].str.contains(regex_pattern)]

    @staticmethod
    def filter_by_opening_tags_all_match(
            puzzles_df: pandas.DataFrame,
            opening_tags: Collection[str]
    ) -> pandas.DataFrame:
        regex_pattern = PuzzleStore.build_regex_pattern(opening_tags)
        expected_matches = len(opening_tags)
        return puzzles_df[puzzles_df['OpeningTags'].str.count(regex_pattern) == expected_matches]

    @staticmethod
    def build_regex_pattern(tags: Collection[str]) -> str:
        regex = r''
        for index, tag in enumerate(tags):
            # \b matches the word boundary, i.e. non-alpha-numerical and whitespace characters,
            # as well as beginning and end of a line
            if index != 0:
                regex += r'|'
            regex += r'\b' + tag + r'\b'
        return regex

    @staticmethod
    def build_none_match_regex_pattern(tags: Collection[str]) ->str:
        # negative lookahead assertion with (?! ... )
        return r'(?!.*(?:' + '|'.join(r'\b' + tag + r'\b' for tag in tags) + r'))'

    @staticmethod
    def combine_tags(own_tags: set[str], other_tags: set[str]) -> set[str]:
        return {'mixed'} \
            if 'mixed' in own_tags or 'mixed' in other_tags \
            else own_tags.union(other_tags)
