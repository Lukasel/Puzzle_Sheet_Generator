from os import PathLike

import pandas

from puzzle_sheet_generator.model.puzzle_store import PuzzleStore


class LichessPuzzleDB(PuzzleStore):
    MAXIMUM_PUZZLE_RATING_DEVIATION = 80
    MINIMUM_PUZZLE_POPULARITY = 20

    def __init__(self, puzzle_db_path : str | PathLike):
        super().__init__(
            pandas.read_csv(puzzle_db_path, header=0, names=self.column_names),
            'Lichess Puzzle Database'
        )

        # todo reduce startup time by having these precalculated
        self.puzzles = self.puzzle_df[(self.puzzle_df['RatingDeviation'] <= self.MAXIMUM_PUZZLE_RATING_DEVIATION)
                                          & (self.puzzle_df['Popularity'] >= self.MINIMUM_PUZZLE_POPULARITY)]
        self.mate_puzzles = self.puzzles[self.puzzles['Themes'].str.contains('mate')]
        self.no_mate_puzzles = self.puzzles[~self.puzzles['Themes'].str.contains('mate')]

    def find_mate(self, moves: int) -> PuzzleStore:
        if moves <= 5:
            mate_puzzles_df = self.mate_puzzles[self.mate_puzzles['Themes'].str.contains(f'mateIn{moves}')]
        else:
            mate_puzzles_df = self.mate_puzzles[(self.mate_puzzles['Moves'].count(' ') + 1) // 2 == moves]
        return PuzzleStore(mate_puzzles_df, 'mate puzzles')

    def find_themes(self, themes: list[str], opening_tag: str | None=None) -> PuzzleStore:
        theme_puzzles = self.no_mate_puzzles
        for theme in themes:
            theme_puzzles = self.find_theme(self.no_mate_puzzles, theme)
        if opening_tag:
            theme_puzzles = self.find_opening(theme_puzzles, opening_tag)
        return PuzzleStore(theme_puzzles, 'theme puzzles')
