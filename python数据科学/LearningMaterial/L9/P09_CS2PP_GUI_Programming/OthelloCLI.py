# OthelloCLI by Martin Lester, University of Reading, 2025.
# You may redistribute under the MIT/X Consortium Licence.

# This is a Python implementation of the classic board game Reversi/Othello.
# This file provides a console implementation.
# However, the game logic is mainly in the separate Othello class,
# so it can be used as the basis of a GUI implementation.

from copy import deepcopy
import random

# This class encapsulates the game logic.
class Othello():

    # Constants for the content of a board grid cell.
    # Maybe these should be Python Enums, but it seems like too much hassle.
    WHITE = 1
    BLACK = -1
    EMPTY = 0
    OOB = 2     # Out Of Bounds

    # Width and height of a new board.
    # These are only used when creating a new board,
    # so if you want to adapt the game to a different board size,
    # you just need to pass the constructor an initial board of the size you want.
    WIDTH = 8
    HEIGHT = 8

    # Constructor.
    # Optionally takes existing board (defaults to new board) and current player (defaults to Black).
    def __init__(self, b=None, p=-1):
        if (b is None):
            # Make a standard starting board.
            self.board = [[0 for y in range(Othello.WIDTH)] for x in range(Othello.HEIGHT)]
            self.board[3][3] = Othello.BLACK
            self.board[4][4] = Othello.BLACK
            self.board[3][4] = Othello.WHITE
            self.board[4][3] = Othello.WHITE
        else:
            # Copy the existing board.
            # Must use deepcopy() to avoid aliasing.
            self.board = deepcopy(b)
        
        self.player = p

    # Return a new Othello game object with no shared state.        
    def clone(self):
        return Othello(self.board, self.player)


    # Return the opponent (who is not currently due to play).
    def opponent(self):
        return self.player * -1

    # Return the string "Black" or "White", indicating the current player's colour,
    # or (if passed) the colour of a specific player.
    def player_name(self, p=None):
        if p is None:
            p = self.player
        if p == Othello.BLACK:
            return "Black"
        else:
            return "White"
    
    # Is (x,y) a legal move?
    def legal_move(self, x, y):
        return self.clone().move(x, y)

    # Attempt to place a disc on (x,y) and flip discs and player as appropriate.
    # Returns True if move was legal and successful.
    # Returns False if move was illegal, in which case board is unchanged.
    def move(self, x, y):
        flipped = False     # Was the move successful?

        # Check if the target cell is empty; if not, move fails.
        if self.get_cell(x, y) != Othello.EMPTY:
            return False
        # But don't set the target cell yet.
        # Avoid making any changes to the board until we are sure the move is legal.

        # Iterate over all 8 possible directions (horizontal, vertical, diagonal).
        # A direction is defined by a step change in x-ordinate and y-ordinate...
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # ...of which at least one must be non-zero.
                if dx == 0 and dy == 0:
                    continue

                # Look at the first cell in the direction.
                (tryx, tryy) = (x + dx, y + dy)
                # If it isn't an opponent disc, move onto the next direction.
                if self.get_cell(tryx, tryy) != self.opponent():
                    continue

                # Keep going in that direction until the first non-opponent disc.
                # (Could be current player's disc, empty, or out of bounds).                
                while self.get_cell(tryx, tryy) == self.opponent():
                    (tryx, tryy) = (tryx + dx, tryy + dy)

                # If the line doesn't end with a current player disc, there are no flips.
                # So move onto the next direction.
                if self.get_cell(tryx, tryy) != self.player:
                    continue

                # At this point, we know that a flip will occur.
                flipped = True
                # Step backwards to the last opponent disc.
                (tryx, tryy) = (tryx - dx, tryy - dy)

                # Keep going backwards, flipping discs as we go,
                # until we get back to the starting point (which will be empty).
                while (self.get_cell(tryx, tryy) == self.opponent()):
                    self.set_cell(tryx, tryy, self.player)
                    (tryx, tryy) = (tryx - dx, tryy - dy)

        # Now we have looked at all directions.
        # If at least one counter was flipped, the move was legal.
        # So finally we can fill the target grid cell.
        # (This is subtly different from the algorithm you might derive directly from
        # the rules, where you would place the disc in the target cell before flipping.)
        if flipped:
            self.set_cell(x, y, self.player).flip_player()

        # Return whether the move was legal.
        return flipped
    
    # Can the current player move anywhere?
    def can_move(self):
        for x in range(0, self.width()):
            for y in range(0, self.height()):
                if self.legal_move(x, y):
                    return True
        return False

    # Is the game over (meaning that neither player has a legal move)?
    def game_over(self):
        return self.can_move() == False and self.clone().flip_player().can_move() == False

    # Attempt to pass play. Return True if successful, or False otherwise.
    # (This is not called "pass" because that is a reserved word in Python.)
    def skip(self):
        if self.can_move() or self.game_over():
            return False
        self.flip_player()
        return True

    # Count scores and return the winner of the game (Othello.BLACK or Othello.WHITE),
    # or Othello.EMPTY in the rare case of a tie.
    def winner(self):
        net = self.net_score(self.player)
        if net > 0:
            return self.player
        if net < 0:
            return self.opponent()
        return Othello.EMPTY
    
    # Count the current score of the specified player.
    def score(self, p):
        return sum(map(lambda row : row.count(p), self.board))

    # Count the net score of the specified player.
    def net_score(self, p):
        return sum(map(lambda row : sum(row), self.board)) * p

    # Use simple heuristic algorithm to suggest best possible move.
    # Returns (possibly empty) list of weighted score gain and corresponding move.
    # PREVIEW: NOT YET TESTED.
    def heuristic_moves(self):
        # Algorithm adapted from a program by Graham Charlton via Tim Hartnell.
        current_score = self.score(self.opponent())
        for x in range(0, self.width()):
            for y in range(0, self.height()):
                o = self.clone()
                if not o.move(x, y):
                    continue

                # Count pieces flipped.
                gain = current_score - o.score(self.opponent())

                # If move is on row/column next to an edge, halve score gain.
                # (Rationale: This space is likely to be flipped by an edge move,
                # after which it will be difficult to flip back.)
                if x == 1 or y == 1 or x == self.width()-2 or y == self.height()-2:
                    gain = gain / 2
                # Otherwise, if move is on row/column on an edge, double score gain.
                # (Rationale: This space is unlikely to be flipped.)
                elif x == 0 or y == 0 or x == self.width()-1 or y == self.height()-1:
                    gain = gain * 2
                    
                yield (gain, (x,y))

    # Find the heuristic best possible moves and choose one at random.
    # PREVIEW: NOT YET TESTED.
    def heuristic_hint(self):
        # Calculate all heuristic scores.
        all_scores = self.heuristic_moves()
        # If no legal move, return None.
        if len(all_scores) == 0:
            return None
        # Find the maximum heuristic score.
        max_score = max(all_scores, key = lambda m : m[0])
        # Filter out just the moves that give the maximum score.
        max_scores = filter(lambda m : m[0] == max_score, all_scores)
        # Return a move at random.
        return random.choice(max_scores)[1]
        
    # Helper function for min_max_score().
    # Try all possible moves, recursing with decreased depth.
    # Returns a list of estimated scores and corresponding moves.
    # PREVIEW: NOT YET TESTED.
    def min_max_moves(self, depth):
        for x in range(0, self.width()):
            for y in range(0, self.height()):
                o = self.clone()
                if not o.move(x, y):
                    continue
                # This returns a likely opponent score and list of likely moves.
                min_scores = o.min_max_score(depth-1)
                # Discard the list of oppoent moves, and yield the player's score and move.
                yield (min_scores[0] * -1, (x,y))
    
    # Use min-max algorithm to suggest best possible move.
    # Returns estimated score and (possibly empty) list of moves achieving it.
    # PREVIEW: NOT YET TESTED.
    def min_max_score(self, depth):
        # Base case: Just return the current score, with no moves required.
        if depth == 0:
            return (self.net_score(self.player), [])

        # Special case: No legal move.        
        if not self.can_move():
            # If it is the end of the game, treat as the base case.
            if self.game_over():
                return (self.net_score(self.player), [])
            # Otherwise, pass to the opponent and recurse at next depth.
            else:
                # We still need to flip the score, as it is for the opponent.
                return (self.clone().flip_player().min_max_score(depth-1)[0] * -1, [])

        # Main case: Legal moves available, and not at bottom of search tree.
        # Create a list of estimated scores for all legal moves.
        all_scores = self.min_max_moves(depth)
        # Find the maximum score for the current player.
        max_score = max(all_scores, key = lambda m : m[0])
        # Filter out and return just the moves that give the maximum score.
        max_scores = filter(lambda m : m[0] == max_score, all_scores)
        return (max_score, map(lambda m : m[1], max_scores))

    # Find the estimated best possible moves and choose one at random.
    # PREVIEW: NOT YET TESTED.
    def min_max_hint(self, depth):
        random.choice(self.min_max_score(depth)[1])

    # Change whose turn it is. Used mainly after making a move.
    # For convenience, returns self, so other methods can be chained afterwards.
    def flip_player(self):
        self.player = self.opponent()
        return self
    
    # Primitive accessor method to set contents of board cell (x,y) to player p.
    # For convenience, returns self, so other methods can be chained afterwards.
    def set_cell(self, x, y, p):
        self.board[x][y] = p
        return self

    # Primitive accessor method to get contents of board cell (x,y).
    # Returns Othello.OOB if the co-ordinates were out of bounds (off the board).
    def get_cell(self, x, y):
        if x < 0 or y < 0:
            return Othello.OOB
        if x >= self.width() or y >= self.height():
            return Othello.OOB
        return self.board[x][y]

    # Returns the width of the board.    
    def width(self):
        return len(self.board[0])
    
    # Returns the height of the board.
    def height(self):
        return len(self.board)

# Console interface to game logic.    
if __name__ == "__main__":
    # Instantiate the game board.
    o = Othello()

    # Keep going until the game is over.
    while True:

        # Print column labels for board.        
        print(" ", end="")
        for x in range(0, o.width()):
            print(chr(ord("A") + x), end="")
        print()
        # Print rows of board.
        for y in range(0, o.width()):
            # Print a row label.
            print(y+1, end="")
            for x in range(0, o.height()):
                # Print a cell.
                c = o.get_cell(x, y)
                if (c == o.WHITE):
                    print("@", end="")
                elif (c == o.BLACK):
                    print("O", end="")
                else:
                    print(" ", end="")
            print()

        # Print the scores.
        print()
        print("Scores:")
        print(o.player_name(Othello.BLACK), ":", o.score(Othello.BLACK))
        print(o.player_name(Othello.WHITE), ":", o.score(Othello.WHITE))
        print()

        # Check for end of game.
        if o.game_over():
            break

        # The game is not over, so someone has to move.
        print(o.player_name(), "to move:")

        # First try passing, if it is necessary.
        if o.skip():
            input("No legal move. Press return to pass.")
            continue

        # Otherwise, ask for and play a move.
        while True:
            trymove = input("Enter your move. ").rstrip()
            if len(trymove) != 2:
                print("Enter a letter followed by a number.")
                continue
            # Work out the column index.
            x = ord(trymove[0:1].upper()) - ord("A")
            if x < 0 or x >= o.width():
                print("Invalid column.")
                continue
            # Work out the row index.
            y = ord(trymove[1:2]) - ord("1")
            if y < 0 or y >= o.height():
                print("Invalid row.")
                continue
            # Check the move is valid.
            if not o.legal_move(x, y):
                print("Illegal move.")
                continue
            # Play the move.
            o.move(x, y)
            break
        
        # Loop back for the next turn of the game.

    # Print the winner.      
    winner = o.winner()
    if winner == Othello.EMPTY:
        print("It is a tie!")
    else:
        print(o.player_name(winner), "wins.")

