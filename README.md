# Puzzle Sheet Generator

A command line program for the creation of chess puzzle PDF-sheets. 
Create puzzle sheets either from the lichess puzzle database or from FEN strings.

## Installation
Download the Lichess puzzles database from https://database.lichess.org/#puzzles and place it unzipped in the `data` directory.

Then run in terminal in this project's main directory:
```commandline
pip install .
```

## Usage

The program is designed to run as an interactive CLI app, so that the puzzle db stays in memory
and doesn't have to be reloaded all the time.
Run 
```commandline
puzzle_sheet_generator
```
to start the interactive CLI.

On start-up the program loads its config and the lichess database, then waits for user commands.

### Concepts:
- Store: A set of puzzles. Subset of the lichess puzzle database obtained by filtering via user specified criteria.
- Sheet: A set of up to 12 puzzles, FEN strings or SVGs and some metadata, that can be printed as a PDF file.
         The puzzles in a sheet can be obtained by sampling from a store, remixing existing sheets and manually entering individual FENs or SVGs.

### Configuration
The apps configuration should be placed in the OS standard location (e.g. /home/<user>/.config/puzzle_sheet_generator on a Linux system).
Possible configurations:
- path to lichess puzzle database
- flag whether to automatically save all created sheets
- board colors

### Commands:
- config: Change the programs configuration
- config-default: Restore the default configuration
- list: show all available sheets or stores
  - `list sh` to show sheets
  - `list st` to show stores
- show: show a specific sheet or store
  - `show <id_or_name>`
- delete: delete a sheet or store
  - `delete <id_or_name>`
- Store specific commands:
  - filter: create a store of puzzles by filtering from the lichess database or an existing store
    - `filter <from_store> <new_store_name>` with options:
      - `-t <theme_1> <additional_theme>*`: themes have to spelled as in the lichess puzzle database. If multiple themes are supplied, a puzzle has to match all of them.
      - `-e <theme_1> <additional_theme>*`: excluded themes. Puzzles that match any of them will be filtered out.
      - `-r (<mean_rating> | <min_rating> <max_rating>)`: mean_rating results in `min_rating = mean_rating - 100` and `max_rating = mean_rating + 100`
      - `-m (<exact_number_of_moves> | <min_moves> <max_moves>)`
      - `-o <opening_tag>`: currently not working properly
  - sample: create a new sheet or add to a sheet by sampling a given number of puzzles from a store
    - `sample <from_store> <into_sheet> [-a <amount of puzzles>]`
  - union: unite two puzzle stores to create a mixed set of puzzles
    - `union <store_1> <store_2> <name_of_new_store>`
- Sheet specific commands:
  - add-to: manually add a new element to a sheet in form of a lichess puzzle (provide puzzle id) or FEN
    - `add-to <sheet> <puzzle>`
  - copy: Create a new sheet with the same elements
    - `copy <sheet> <new_sheet_name>`
  - remove: remove an element from a sheet
    - `remove <sheet> <puzzle>` with `<puzzle>` being either a lichess puzzle id or the index in the puzzle sheet
  - reorder: reorder elements in a sheet
    - `reorder <sheet> <index1> <index2>`
  - name: Change the name of a sheet or store
  - header: Specify what will be printed in the header above the puzzles
    - `header -l <left-header> -r <right-header>`
  - load: load a saved sheet or a directory of saved sheets
  - save: save a sheet, so it can be reused across multiple sessions
- print: create a PDF file from a sheet
  - `print <sheet> <path/to/file.pdf>` with options:
    - `-l (6 | 12)` explicitly choose a layout with 6 or 12 puzzles on one page
    - `--left-header` set the text printed in the left header
    - `--right-header` set the text printed in the right header

## Development Setup

In the repositories main directory set up a new python virtual environment:
```commandline
python -m venv .venv
```
and activate it with `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows).

Install in development mode via pip:
```commandline
pip install --editable .
```
