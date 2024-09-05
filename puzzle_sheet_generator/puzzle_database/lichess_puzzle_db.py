import pandas


class LichessPuzzleDB:
    def __init__(self, config: dict):
        self.column_names = (
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
        self.puzzles = pandas.read_csv(config["lichess_puzzle_db_path"], header=0, names=self.column_names)
        # todo reduce startup time by having these precalculated
        self.puzzles = self.puzzles[(self.puzzles['RatingDeviation'] <= 80)
                                          & (self.puzzles['Popularity'] >= 20)]
        self.mate_puzzles = self.puzzles[self.puzzles['Themes'].str.contains('mate')]
        self.no_mate_puzzles = self.puzzles[~self.puzzles['Themes'].str.contains('mate')]

    def find_mate(self, moves: int):
        if moves <= 5:
            return self.mate_puzzles[self.mate_puzzles['Themes'].str.contains(f'mateIn{moves}')]
        return self.mate_puzzles[(self.mate_puzzles['Moves'].count(' ') + 1) // 2 == moves]

    def find_themes(self, themes: list[str], opening_tag: str | None=None):
        theme_puzzles = self.no_mate_puzzles
        for theme in themes:
            theme_puzzles = self.find_theme(self.no_mate_puzzles, theme)
        if opening_tag:
            theme_puzzles = self.find_opening(theme_puzzles, opening_tag)
        return theme_puzzles

    @staticmethod
    def filter_by_rating(puzzles_df: pandas.DataFrame, min_rating: int, max_rating: int):
        return puzzles_df[(puzzles_df['Rating'] >= min_rating)
                          & (puzzles_df['Rating'] <= max_rating)]

    @staticmethod
    def find_theme(puzzles_df: pandas.DataFrame, theme: str):
        return puzzles_df[puzzles_df['Themes'].str.contains(theme)]

    @staticmethod
    def find_opening(puzzles_df: pandas.DataFrame, opening_tag: str):
        return puzzles_df[puzzles_df['OpeningTags'].str.contains(opening_tag)]
