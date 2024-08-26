"""Column names and puzzle themes in the lichess puzzle database."""

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

advantage_goal_themes = {
    'equality',
    'advantage',
    'crushing',
    'mate'
}

endgame_type_theme = {
    'bishopEndgame',
    'knightEndgame',
    'pawnEndgame',
    'queenEndgame',
    'queenRookEndgame',
    'rookEndgame',
}

game_stage_themes = {
    'endgame',
    'middlegame',
    'opening',
}

length_themes = {
    'long',
    'oneMove',
    'short',
    'veryLong',
}

player_themes = {
    'master',
    'masterVsMaster',
    'superGM',
}

mate_length_themes = {
    'mateIn1',
    'mateIn2',
    'mateIn3',
    'mateIn4',
    'mateIn5',
}

mate_type_themes = {
    'anastasiaMate',
    'arabianMate',
    'backRankMate',
    'bodenMate',
    'doubleBishopMate',
    'dovetailMate',
    'hookMate',
    'smotheredMate',
}

move_type_themes = {
    'castling',
    'enPassant',
}

tactical_themes = {
    'advancedPawn',
    'attackingF2F7',
    'attraction',
    'capturingDefender',
    'clearance',
    'defensiveMove',
    'deflection',
    'discoveredAttack',
    'doubleCheck',
    'exposedKing',
    'fork',
    'hangingPiece',
    'interference',
    'intermezzo',
    'kingsideAttack',
    'mate',
    'pin',
    'promotion',
    'queensideAttack',
    'quietMove',
    'sacrifice',
    'skewer',
    'trappedPiece',
    'underPromotion',
    'xRayAttack',
    'zugzwang'
}

all_puzzle_themes = (
        advantage_goal_themes
        | endgame_type_theme
        | game_stage_themes
        | length_themes
        | player_themes
        | mate_length_themes
        | mate_type_themes
        | move_type_themes
        | tactical_themes
)
