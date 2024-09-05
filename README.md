# Puzzle Sheet Generator

A command line program for the creation of chess puzzle PDF-sheets. 
Create puzzle sheets either from the lichess puzzle database or from FEN strings.

## Setup

In the repositories main directory set up a new python virtual environment:
```commandline
python -m venv .venv
```
and activate it with `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows).

Install dependencies via pip:
```commandline
pip install -r requirements.txt
```

Download the Lichess puzzles database from https://database.lichess.org/#puzzles and place it unzipped in the `data` directory.

## Usage

CLI still in progress

## Developement

To update dependencies via pip:
```commandline
pip-compile -U
```
