"""
6.101 Lab 7: Sam Vinu-Srivatsan
Six Double-Oh Mines
"""
#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows,ncolumns),mines)

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game,(row,col))

def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game,all_visible)

def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    # call the render_2d_locations function and join the individual lists
    rendered_board = render_2d_locations(game,all_visible)
    all_rows = [] # a list of row strings
    for row in rendered_board:
        all_rows.append( "".join(row))
    # all_rows: [".31_"  , "__1_"]
    asc_char = "" # string to concatenate to
    last = all_rows.pop()
    for row in all_rows:
        asc_char += row + "\n"
    asc_char += last
    return asc_char

# N-D IMPLEMENTATION

def get_value_nd(board,coordinates):
    """
    A function that, given an N-d array and a tuple/list of coordinates,
    returns the value at those coordinates in the array.
    """
    # base case is 0D board: 0
    if not isinstance(board,list): # value not list
        # coordinates would only have 1 coordinate
        return board

    # recursive case is not a 1D board
    new_board = board[coordinates[0]]
    # where new_board is a list of more nested lists
    return get_value_nd(new_board,coordinates[1:])

def set_value_nd(board,coordinates,value):
    """
    A function that, given an N-d array, a tuple/list of coordinates,
    and a value, replaces the value at those coordinates in the array
    with the given value.
    """
    # base case is 1D board: [a,b,c,d]
    if not isinstance(board[0],list): # no more nested lists
        board[coordinates[0]] = value
    else:
        # recursive case is not a 1D board
        new_board = board[coordinates[0]]
        set_value_nd(new_board,coordinates[1:],value)

def create_nd_array(dimensions,value):
    """
    A function that, given a list of dimensions and a value,
    creates a new N-d array with those dimensions, where each value in
    the array is the given value.
    """
    # base case is 1D
    if len(dimensions) == 1: # if there is only 1 dimension
        return [value]*dimensions[0]
    # if there are more dimensions, keep popping dimensions
    new_board = []
    for _ in range(dimensions[0]):
        new_board.append(create_nd_array(dimensions[1:],value))
    return new_board

def get_game_state(game):
    """
    A function that, given a game dictionary, returns the state of that game
    ('ongoing', 'defeat', or 'victory').
    """
    victory = True
    # iterate through all safe squares
    for coord in get_all_coordinates(game["dimensions"]):
        if get_value_nd(game["board"],coord) != ".": # if not mine
            if not get_value_nd(game["visible"],coord): # hidden safe square
                victory = False
                return "ongoing"
    if victory:
        return "victory"

def get_all_coordinates(dimensions):
    """
    Given the dimensions of a game, return a list of tuples of all possible
    coordinate combinations within that game board recursively.
    """
    # base case 1D, dimension is a tuple with 1 element
    if len(dimensions) == 1:
        all_coords = []
        for coord in range(dimensions[0]):
            all_coords.append((coord,))
        return all_coords
    # recursive case
    all_coords = []
    first_coords = list(range(dimensions[0]))
    rest_coords = get_all_coordinates(dimensions[1:])
    for coor in first_coords: # each element is a number
        for r in rest_coords: # each element is a tuple
            all_coords.append(((coor,)+r))
    return all_coords

def get_neighbors(coordinate,dimension):
    """
    A function that returns all the neighbors of
    a given set of coordinates in a given game.
    """
    def neighbors(coordinate,dimension):
        # base case is 1D game
        if len(coordinate) == 1:
            # coordinate = (x,)
            return {(coordinate[0]+x,) for x in [-1,0,1]}
        # recursive case
        neighbors = set()
        first = coordinate[0]
        rest = coordinate[1:]
        neighbor_coords = get_neighbors(rest,dimension[1:])
        for offset in [first+x for x in [-1,0,1]]:
            for rest_coords in neighbor_coords: # neighbor already tuple
                neighbors.add((offset,)+rest_coords)
        return neighbors

    # remove invalid coordinate
    valid_neighbors = set()
    for neighbor_coord in neighbors(coordinate,dimension):
        if is_valid_coordinate(neighbor_coord,dimension):
            valid_neighbors.add(neighbor_coord)
    return valid_neighbors

def is_valid_coordinate(coordinate,dimensions):
    """
    Return a Boolean indicating whether coordinate is within valid bounds or not.
    """
    for n_coord,n_d in zip(coordinate,dimensions):
        # coordinate of that n dimension is NOT valid range for that dimension
        if not 0 <= n_coord < n_d:
            return False
    return True


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    # create game board and visibility arrays
    board = create_nd_array(dimensions,0)
    visible = create_nd_array(dimensions,False)

    # set all values of board
    # set mines
    for mine_coord in mines:
        set_value_nd(board,mine_coord,".")
        # set neighboring safe square values
        for neighbor_coord in get_neighbors(mine_coord,dimensions):
            val = get_value_nd(board,neighbor_coord)
            if val != ".":
                # increment the value of neighbor +=1
                set_value_nd(board,neighbor_coord,val+1)
    return {
            "dimensions": dimensions,
            "board": board,
            "visible": visible,
            "state": "ongoing",
        }

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    def dig_helper(coordinates):
        revealed = 0 # revealed in this turn
        # if the game is already over
        if game["state"] == "defeat" or game["state"] == "victory":
            return 0

        # if game still in play: first reveal the assigned square if not yet revealed
        if not get_value_nd(game["visible"],coordinates):
            set_value_nd(game["visible"],coordinates,True)
            revealed = 1
        else: # already visible
            return 0

        board_value = get_value_nd(game["board"],coordinates)
        # if we just revealed a mine
        if board_value == ".":
            game["state"] = "defeat"
            return 1

        # row,col value is 0 so no adjacent squares have mines
        if board_value == 0:
            # dig at all neighbors
            for neighbor_coord in get_neighbors(coordinates,game["dimensions"]):
                revealed += dig_helper(neighbor_coord)

        # after all these actions, confirm victory/ongoing
        return revealed

    revealed = dig_helper(coordinates)
    if game["state"] != "defeat":
        game["state"] = get_game_state(game)
    return revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    # if not all tiles are visible yet, create new render board
    render_board = create_nd_array(game["dimensions"],"_")

    # populate the rendered board
    # go through all coordinates. if that that coordinate, visible = True, show
    for coord in get_all_coordinates(game["dimensions"]):
        if get_value_nd(game["visible"],coord) or all_visible: # if visible
            value = get_value_nd(game["board"],coord)
            # value stays the same if mine
            if value == 0:
                value = " "
            elif isinstance(value,int): # another nonzero int
                value = str(value)
            set_value_nd(render_board,coord,value)
    return render_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    # #
    # doctest.run_docstring_examples(
    #    render_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

    # g = {'dimensions': (2, 4, 2),
    #   'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #            [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #  'visible': [[[False, False], [False, True], [False, False],
    #             [False, False]],
    #            [[False, False], [False, False], [False, False],
    #            [False, False]]],
    #  'state': 'ongoing'}
    # # print("NEIGHBORS",get_neighbors((0, 0, 1),g['dimensions']))
    # dig_nd(g, (0, 0, 1))
