"""Tetris clone.
Relies on a grid of spaces.  Each cell in the grid contains one of the following values:
0: This cell is empty.
1: This cell contains part of a dead piece.
2: This cell contains part of a live piece.
"""

import random
import math
import numpy as np
import statistics

# TODOS
# TODO: Put in rotation.
# TODO: Make it GUI-based instead of text-based.
# TODO: Make it time-sensitive, provided that Python's timing isn't so unreliable as to make this impossible.


def create_grid(dimensions):
    """Returns an array of the specified dimensions.
    dimensions: a tuple. (rows, cols)
    """
    rows = dimensions[0]
    cols = dimensions[1]

    # Create list of lists
    tetris_grid = []
    for row in range(rows):
        tetris_grid.append([0] * cols)

    # Convert to numpy array
    tetris_grid = np.array(tetris_grid)
    return tetris_grid


def create_piece(pieces):
    """Creates a new random piece at the top center of the grid and places it under the player's control.
    possible_pieces: a list of the possible pieces, each of which is a numpy array.
    Returns True if the new piece doesn't fit.  This means that the player has lost.  If this happens, resolve_loss()
    should be called.
    """
    global grid

    # Choose a piece.  Pieces are all defined by a 2x4 grid.
    piece = random.choice(pieces)

    # Add the piece with the top left corner at row 0, col floor(cols/2)-2.
    grid[0:2, math.floor(len(grid[0]) / 2) - 2:math.floor(len(grid[0]) / 2) + 2] = grid[0:2, math.floor(len(grid[0]) / 2) - 2:math.floor(len(grid[0]) / 2) + 2] + piece

    # Check to see if adding the piece results in a loss, due to overlapping an existing piece (this is true if and only if there exists 1 or more cells containing 3).
    if 3 in grid:   # If so, return True.
        return True
    else:   # If not, return False.
        return False


def rotate_piece(direction):    # TODO
    """Rotates the active piece, if possible.
    direction: "ccw" or "cw"
    """
    global grid

    grid_temp = np.copy(grid)

    # Find the coordinates of the centroid of the live piece, rounded to the nearest row and column.
    piece_coords = [(row, column) for row in range(np.shape(grid_temp)[0]) for column in range(np.shape(grid_temp)[1]) if grid_temp[row, column] == 2]
    piece_row_coords, piece_column_coords = [element[0] for element in piece_coords], [element[1] for element in piece_coords]
    centroid_coords = (round(statistics.mean(piece_row_coords)), round(statistics.mean(piece_column_coords)))
    print(centroid_coords)

    # In grid_temp, turn 1 cell of the live piece closest to the centroid into a 6.

    # Create grid_rotation, which is grid_temp but with the 1s turned into 0s.  Then rotate grid_rotation in the desired direction ("ccw" or "cw").

    # Line up the grid_rotation over grid_temp, such that the 6s line up, and add them together.

    # Check to see if this rotation is valid (ie, has the same number of 2s as before).  If so, update grid to match grid_temp.


def shift_piece(direction):
    """Shifts the active piece 1 space to the left or right, if possible.
    direction: "l" or "r"
    """
    global grid

    if not isinstance(direction, str):
        raise TypeError("direction must be a string.")

    grid_temp = np.copy(grid)

    if direction == "l":    # Shift all 2s one space to the left.
        if 2 not in grid_temp[:, 0]: # Check to make sure no part of the active shape is in the leftmost column.
            for row in range(np.shape(grid_temp)[0]):
                for col in range(np.shape(grid_temp)[1]):
                    if grid_temp[row, col] == 2:
                        grid_temp[row, col-1] = grid_temp[row, col-1] + 2
                        grid_temp[row, col] = 0
    elif direction == "r":  # Shift all 3s one space to the right.
        if 2 not in grid_temp[:, -1]:    # Check to make sure no part of the active shape is in the rightmost column.
            grid_temp = np.fliplr(grid_temp)
            for row in range(np.shape(grid_temp)[0]):
                for col in range(np.shape(grid_temp)[1]):
                    if grid_temp[row, col] == 2:
                        grid_temp[row, col - 1] = grid_temp[row, col - 1] + 2
                        grid_temp[row, col] = 0
            grid_temp = np.fliplr(grid_temp)
    else:
        raise ValueError("direction must be either 'l' or 'r'.")

    # If there are no 3s, update grid to match grid_temp.
    if 3 not in grid_temp:
        grid = np.copy(grid_temp)


def descend_piece():
    """Descends the piece 1 space down.
    Returns True if the piece is now dead, and kills the piece.
    Else, returns False.
    """
    global grid

    # Check if any elements of the active piece are on the bottom layer.  If so, kill the piece and return True.
    if 2 in grid[-1, :]:
        grid = np.where(grid != 2, grid, 1)    # Set all 2s in grid to 1s.
        return True

    # Create a grid_temp and rotate it 90 degrees clockwise.
    grid_temp = np.copy(grid)
    grid_temp = np.rot90(grid_temp, axes=(1, 0))

    # Shift all live pieces in grid_temp 1 place to the left.
    for row in range(np.shape(grid_temp)[0]):
        for col in range(np.shape(grid_temp)[1]):
            if grid_temp[row, col] == 2:
                grid_temp[row, col - 1] = grid_temp[row, col - 1] + 2
                grid_temp[row, col] = 0

    # Rotate grid_temp back, 90 degrees counterclockwise.
    grid_temp = np.rot90(grid_temp)

    # If the number of 2s in grid_temp is the same as in grid, update grid to match grid_temp, and return False.
    # Else, grid should not be updated to match grid_temp; kill the piece in grid, and return True.
    if np.count_nonzero(grid_temp == 2) == np.count_nonzero(grid == 2):
        grid = np.copy(grid_temp)
        return False
    else:
        grid = np.where(grid != 2, grid, 1)    # Set all 2s in grid to 1s.
        return True


def check_for_tetrises():
    """Checks the board for any completed tetrises.
    All pieces must be dead at this point.
    Returns a list of indices for the rows where tetrises have occurred (an empty list if none have occurred).
    """
    global grid

    tetris_rows = []    # This will accumulate the indices of rows where tetrises have occurred.

    for row in range(np.shape(grid)[0]):
        if False not in (grid[row, :] == np.array([1] * np.shape(grid)[1])):   # If this row is all 1s:
            tetris_rows.append(row)

    return tetris_rows


def resolve_tetrises(tetris_rows):
    """Resolves completed tetrises by deleting them and descending blocks above them, and increases the player's score
    by however many tetrises were resolved.
    tetris_rows: A list of rows where tetrises have occurred (empty if none have occurred).
    """
    global grid
    global score

    for row_to_delete in tetris_rows:
        # Shift down all the rows above, replacing row_to_delete in the process.
        grid[1:row_to_delete+1, :] = grid[:row_to_delete]

        # Set all entries in the top row to 0.
        grid[0, :] = 0

        # Increase score by 1.
        score = score + 1


def take_input():
    """Asks the player for a direction, then calls the appropriate helper function.
    a: calls shift_piece("l")
    d: calls shift_piece("r")
    s: calls descend_piece()
    q: calls rotate_piece("ccw")
    e: calls rotate_piece("cw")

    Returns whatever is returned by the appropriate helper function.
    """
    global grid

    response = input("Choose a (left), d (right), s (down), q (rotate ccw), or e (rotate cw): ")

    if response == "a":
        return shift_piece("l")
    elif response == "d":
        return shift_piece("r")
    elif response == "s":
        return descend_piece()
    elif response == "q":
        return rotate_piece("ccw")
    elif response == "e":
        return rotate_piece("cw")
    else:
        print("Invalid response.")


def resolve_loss(player_score):
    """Shows the player their final score and ends the game."""
    print("GAME OVER\tYour score: " + str(player_score))
    exit()


# Initialize.
score = 0
possible_pieces = [np.array([[2, 2, 2, 2], [0, 0, 0, 0]]),
                   np.array([[2, 0, 0, 0], [2, 2, 2, 0]]),
                   np.array([[0, 0, 0, 2], [0, 2, 2, 2]]),
                   np.array([[0, 2, 2, 0], [0, 2, 2, 0]]),
                   np.array([[0, 2, 2, 0], [2, 2, 0, 0]]),
                   np.array([[0, 2, 2, 0], [0, 0, 2, 2]]),
                   np.array([[0, 2, 0, 0], [2, 2, 2, 0]])]
grid = create_grid((20, 10))

# Scripts for testing go here.
create_piece(possible_pieces)
print(grid)
rotate_piece("ccw")

# Game script.
"""
while True:
    if not create_piece(possible_pieces):   # If creating the new piece does not cause a loss:
        while True:
            print(grid)
            if take_input():    # If the helper function that take_input() called returned True (ie if the piece is now dead):
                resolve_tetrises(check_for_tetrises())
                break
    else:   # If creating the new piece causes a loss:
        resolve_loss(score)
        break
"""
