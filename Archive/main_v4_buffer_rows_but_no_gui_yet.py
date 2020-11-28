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
# TODO: Make it GUI-based instead of text-based.
# TODO: Make it real-time, provided that Python's timing isn't so unreliable as to make this impossible.


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
    Returns True if the new piece doesn't fit, or if there are any dead pieces in the top 2 rows (ie the buffer rows.
    This means that the player has lost.  If this happens, resolve_loss() should be called.
    """
    global grid

    # Choose a piece.  Pieces are all defined by a 2x4 grid.
    piece = random.choice(pieces)

    # Add the piece with the top left corner at row 0, col floor(cols/2)-2.
    grid[0:2, math.floor(len(grid[0]) / 2) - 2:math.floor(len(grid[0]) / 2) + 2] = grid[0:2, math.floor(len(grid[0]) / 2) - 2:math.floor(len(grid[0]) / 2) + 2] + piece

    # Check if resolve_loss() should be called/  Else, return false.
    if 3 in grid:   # If the new piece overlaps a dead piece, return True so that resolve_loss() will be called.
        return True
    if 1 in grid[0:2, :]:   # If there's a dead piece in a buffer row, return True so that resolve_loss() will be called.
        return True
    else:   # If not, return False.
        return False


def rotate_piece(direction, wall_kick_test=None):
    """Rotates the active piece, if possible.
    direction: "ccw" or "cw"
    wall_kick_test indicates whether this particular run is for a wall-kick test.  It is either None, "l" for the left wall-kick test, or "r" for the right wall-kick test.
    """
    global grid

    grid_temp = np.copy(grid)

    # Find the coordinates of the centroid of the live piece, and round either to a cell or a vertex, but not an edge.
    piece_coords = [(row, column) for row in range(np.shape(grid_temp)[0]) for column in range(np.shape(grid_temp)[1]) if grid_temp[row, column] == 2]
    piece_row_coords, piece_column_coords = [element[0] for element in piece_coords], [element[1] for element in piece_coords]
    centroid_coords = [statistics.mean(piece_row_coords), statistics.mean(piece_column_coords)]
    # If centroid_coords is exactly on a corner, leave it there.  Otherwise, round it to the nearest cell.  # TODO: Use voronoi to round to the nearest cell or corner.
    if not (centroid_coords[0] % 1 == 0.5 and centroid_coords[1] % 1 == 0.5):
        centroid_coords[0] = math.ceil(centroid_coords[0])
        centroid_coords[1] = math.ceil(centroid_coords[1])
    #centroid_coords = (round(statistics.mean(piece_row_coords)*2)/2, round(statistics.mean(piece_column_coords)*2)/2)

    # Create rotation_box, a matrix encompassing the shape to be rotated, centered on centroid_coords.
    boundary_up, boundary_down, boundary_left, boundary_right = round(centroid_coords[0]), round(centroid_coords[0]), round(centroid_coords[1]), round(centroid_coords[1])
    # Determine how far up to go.   # TODO: Also put wall kicks here.
    while True:
        if (boundary_up != 0) and (2 in grid_temp[boundary_up - 1, :]):  # Keep pushing boundary_up upward until doing so would enter into a column that contains no live pieces.
            boundary_up = boundary_up - 1
        else:
            break
    # Determine how far down to go.
    while True:
        if (boundary_down != np.shape(grid_temp)[0]-1) and (2 in grid_temp[boundary_down + 1, :]):  # Keep pushing boundary_down downward until doing so would enter into a column that contains no live pieces.
            boundary_down = boundary_down + 1
        else:
            break
    # Determine how far left to go.
    while True:
        if (boundary_left != 0) and (2 in grid_temp[:, boundary_left - 1]):     # Keep pushing boundary_left leftward until doing so would enter into a column that contains no live pieces.
            boundary_left = boundary_left - 1
        else:
            break
    # Determine how far right to go.
    while True:
        if (boundary_right != np.shape(grid_temp)[1]-1) and (2 in grid_temp[:, boundary_right + 1]):    # Keep pushing boundary_right rightward until doing so would enter into a column that contains no live pieces.
            boundary_right = boundary_right + 1
        else:
            break
    # Create rotation_box
    rotation_box = np.copy(grid_temp[boundary_up:boundary_down+1, boundary_left:boundary_right+1])
    rotation_box[rotation_box != 2] = 0     # Remove all non-2 elements from rotation_box.

    # Subtract the 2s from grid_temp, then rotate rotation_box 90 degrees in the requested direction.
    grid_temp[grid_temp == 2] = 0
    if direction == "ccw":
        rotation_box = np.rot90(rotation_box)
    elif direction == "cw":
        rotation_box = np.rot90(rotation_box, axes=(1, 0))

    # Re-add rotation_box to grid_temp such that the centroid is in the same position as before (be it in a cell or vertex).
    # Find start_row and start_column, the coordinates of the top-left-most cell to begin adding rotation_box to grid_temp.
    start_row, start_column = round(centroid_coords[0] - 0.5*np.shape(rotation_box)[0]), round(centroid_coords[1] - 0.5*np.shape(rotation_box)[1])
    # Attempt to add.  If this would result in cells being placed off the screen, then return instead.
    try:
        grid_temp[start_row:start_row+np.shape(rotation_box)[0], start_column:start_column+np.shape(rotation_box)[1]] += rotation_box
    except ValueError:  # TODO: Make wall kicks work here too.  It's more complicated than just removing "return" and uncommenting the following code.
        return
        #if wall_kick_test is None:
            #shift_piece("l")
            #rotate_piece(direction, wall_kick_test="l")
        #elif wall_kick_test == "l":
            #shift_piece("r")
            #rotate_piece(direction, wall_kick_test="r")

    # Check to see if this rotation is valid (ie, has the same number of 2s as before).  If so, update grid to match grid_temp.  If not, try shifting the rotated piece left and right to see if those work, and implement those instead if they do.
    if np.count_nonzero(grid_temp == 2) == np.count_nonzero(grid == 2):
        grid = np.copy(grid_temp)
    elif wall_kick_test is None:
        shift_piece("l")
        rotate_piece(direction, wall_kick_test="l")
    elif wall_kick_test == "l":
        shift_piece("r")
        rotate_piece(direction, wall_kick_test="r")



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
grid = create_grid((22, 10))    # Include an extra 2 for buffer rows

# Scripts for testing go here.
grid[:, 0] = 1
grid[:, -1] = 1

# Game script.
while True:
    if not create_piece(possible_pieces):   # If creating the new piece does not cause a loss:
        while True:
            print(grid[2:, :])
            if take_input():    # If the helper function that take_input() called returned True (ie if the piece is now dead):
                resolve_tetrises(check_for_tetrises())
                break
    else:   # If creating the new piece causes a loss:
        resolve_loss(score)
        break
