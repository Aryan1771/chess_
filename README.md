# Chess

Chess is a Python Tkinter chess application with image-based pieces, Stockfish integration, move highlighting, timers, board flipping, PGN save/load support, and adjustable AI difficulty.

## Features

- Graphical chess board built with Tkinter
- Piece images loaded from the `images/` directory
- Stockfish engine integration for AI moves
- Adjustable AI Elo/skill slider
- Timed and untimed game modes
- Legal move handling through the `python-chess` library
- Last-move highlighting and check highlighting
- Board flip shortcut
- Undo support
- PGN save and load support
- Optional opening book path support
- Sound feedback through Windows `winsound`

## Tech Stack

- Python
- Tkinter
- Pillow
- python-chess
- stockfish Python package
- Stockfish engine binary

## Project Structure

```text
chessgame.py             Main application
images/                  White and black chess piece images
chess_icon.ico           Application icon
music.strudel            Audio/music experiment file
```

## Requirements

Install Python dependencies:

```powershell
pip install pillow python-chess stockfish
```

Download a Stockfish engine binary and place it in the project folder with the name:

```text
stockfish
```

On Windows, this may be an executable such as `stockfish.exe`. If you use a different filename, update the `stockfish_path` value in `chessgame.py`.

## Run

```powershell
python chessgame.py
```

## Keyboard Shortcuts

- `Ctrl+Z`: undo the last player/AI move pair
- `F`: flip the board
- `Ctrl+S`: save PGN
- `Ctrl+L`: load PGN

## Notes

This project depends on an external Stockfish binary. The Python package alone is not enough unless the engine executable is available at the configured path.

## License

This repository is licensed under the GPL-3.0 license. See `LICENSE` for details.
