# Puzzle Sheet Generator

A command line program for the creation of chess puzzle PDF-sheets. 
Create puzzle sheets either from the lichess puzzle database or from FEN strings.

## Installation
```commandline
pip install .
```

Download the Lichess puzzles database from https://database.lichess.org/#puzzles and place it unzipped in the `data` directory.

## Usage

CLI still in progress

Idea: Interactive CLI, so we don't have to reload the puzzle db all the time

On start-up the program loads its config and the lichess database, then waits for user commands via interactive cli.

### Concepts:
- Store: A set of puzzles. Subset of the lichess puzzle database obtained by filtering via user specified criteria.
- Sheet: A set of up to 12 puzzles, FEN strings or SVGs and some metadata, that can be printed as a PDF file.
         The puzzles in a sheet can be obtained by sampling from a store, remixing existing sheets and manually entering individual FENs or SVGs.

### Configuration
The apps configuration should be placed in the OS standard location (e.g. /home/<user>/.config/puzzle_sheet_generator on a Linux system).
Possible configurations:
- path to lichess puzzle database
- flag whether to automatically save all created sheets
- 

### Commands:
- config: Change the programs configuration
- filter: create a store of puzzles by filtering from the db or an existing store
- store:
  - sample: create a new sheet or add to a sheet by sampling a given number of puzzles from a store
  - show: show all available stores i.e. subsets of the puzzle db
  - union: unite two puzzle stores to create a mixed set of puzzles
- sheet:
  - add: manually add a new element to a sheet in form of a FEN or SVG
  - copy: Create a new sheet with the same elements
  - remove: remove an element from a sheet
  - reorder: reorder elements in a sheet
  - name: Change the name of a sheet
  - header: Specify what will be printed in the header above the puzzles
  - load: load a saved sheet or a directory of saved sheets
  - save: save a sheet, so it can be reused across multiple sessions
  - show: show all available sheets
- print: create a PDF file from a sheet

## Developement Setup

In the repositories main directory set up a new python virtual environment:
```commandline
python -m venv .venv
```
and activate it with `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows).

Install in development mode via pip:
```commandline
pip install --editable .
```
