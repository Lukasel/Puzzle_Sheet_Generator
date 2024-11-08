from os import PathLike

import pandas

from puzzle_sheet_generator.model.puzzle_store import PuzzleStore
from puzzle_sheet_generator.puzzle_database.lichess_puzzle_db_columns import lichess_puzzle_db_column_names


class LichessPuzzleDB(PuzzleStore):
    MAXIMUM_PUZZLE_RATING_DEVIATION = 80
    MINIMUM_PUZZLE_POPULARITY = 20

    def __init__(self, puzzle_db_path : str | PathLike):
        super().__init__(
            pandas.read_csv(puzzle_db_path, header=0, names=lichess_puzzle_db_column_names),
            'Lichess Puzzle Database'
        )

        # todo reduce startup time by having these precalculated
        self.puzzles = self.puzzle_df[(self.puzzle_df['RatingDeviation'] <= self.MAXIMUM_PUZZLE_RATING_DEVIATION)
                                          & (self.puzzle_df['Popularity'] >= self.MINIMUM_PUZZLE_POPULARITY)]
