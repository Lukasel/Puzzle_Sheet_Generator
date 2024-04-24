"""Generate Chess Puzzle Sheets as PDF files.

Run with::

    $ python -m puzzle_sheet_generator.psg_cli [options] [dest_path]
"""

from pathlib import Path

import puzzle_sheet_generator.puzzle_sheet_generator as puzzle_sheet_generator


__author__ = 'Lukas Malte Monnerjahn'
__all__ = ('puzzle_sheet_generator_command',)


def puzzle_sheet_generator_command():
    import click

    @click.command(context_settings=dict(help_option_names=['-h', '--help']))
    @click.argument(
        'dest_path',
        type=click.Path(dir_okay=False, writable=True, path_type=Path),
    )
    @click.option(
        '--left-header',
        type=click.STRING,
        default="",
        help='Sets the Theme that is printed on the top left of the puzzle sheet.',
    )
    @click.option(
        '--right-header',
        type=click.STRING,
        default="",
        metavar='<right_header>',
        help='Sets the more specific theme or name that is printed on the top right of the puzzle sheet.',
    )
    @click.option(
        '--min-rating',
        '--min-r',
        default=600,
        type=click.IntRange(min=399, max=3333, clamp=True),
        help='Minimum rating of puzzles from the lichess puzzles database',
    )
    @click.option(
        '--max-rating',
        '--max-r',
        default=3000,
        type=click.IntRange(min=399, max=3333, clamp=True),
        help='Maximum rating of puzzles from the lichess puzzles database',
    )
    def cli(dest_path: Path, left_header: str, right_header: str, min_rating: int, max_rating: int):
        """Generate Chess Puzzle Sheets as PDF files."""

        svgs = []
        puzzle_sheet_generator.make_pdf_puzzle_page(dest_path, svgs, left_header, right_header)

    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    puzzle_sheet_generator_command()
