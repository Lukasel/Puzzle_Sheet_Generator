import pandas

class PuzzleStore:
    column_names = (
        'PuzzleId',
        'FEN',
        'Moves',
        'Rating',
        'RatingDeviation',
        'Popularity',
        'NbPlays',
        'Themes',
        'GameUrl',
        'OpeningTags'
    )

    def __init__(self, puzzle_df: pandas.DataFrame, name: str):
        self.puzzle_df = puzzle_df
        self.name = name

    def __len__(self):
        return self.puzzle_df.__len__()

    def get_themes(self):
        # todo
        return "mixed"

    def get_openings(self):
        # todo
        return "mixed"

    def get_min_rating(self):
        return self.puzzle_df['Rating'].min()

    def get_max_rating(self):
        return self.puzzle_df['Rating'].max()

    def get_median_rating(self):
        return self.puzzle_df['Rating'].median()

    @staticmethod
    def filter_by_rating(puzzles_df: pandas.DataFrame, min_rating: int, max_rating: int) -> pandas.DataFrame:
        return puzzles_df[(puzzles_df['Rating'] >= min_rating)
                          & (puzzles_df['Rating'] <= max_rating)]

    @staticmethod
    def find_theme(puzzles_df: pandas.DataFrame, theme: str) -> pandas.DataFrame:
        return puzzles_df[puzzles_df['Themes'].str.contains(theme)]

    @staticmethod
    def find_opening(puzzles_df: pandas.DataFrame, opening_tag: str) -> pandas.DataFrame:
        return puzzles_df[puzzles_df['OpeningTags'].str.contains(opening_tag)]