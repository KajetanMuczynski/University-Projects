import curses
from collections import defaultdict, Counter
import time
messages = []
class Piece:
    """Main piece class, specific piece classes inherit from this one."""
    def __init__(self, type, color, position, status=True, previous_move=None):
        self.type = type
        self.color = color
        self.position = position
        self.status = status
        self.previous_move = position

    def move(self, new_position):
        self.previous_move = self.position
        self.position = new_position

    def get_unicode(self):
        unicode_symbols = {
            'pawn': {'black': '♙', 'white': '♟'},
            'rook': {'black': '♖', 'white': '♜'},
            'knight': {'black': '♘', 'white': '♞'},
            'bishop': {'black': '♗', 'white': '♝'},
            'queen': {'black': '♕', 'white': '♛'},
            'king': {'black': '♔', 'white': '♚'},
        }
        return unicode_symbols[self.type][self.color]

    def __str__(self):
        return self.get_unicode()

    def is_legal_move(self, new_position, positions):
        return False

class Pawn(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('pawn', color, position, status, previous_move)
        self.just_moved_two = False
        self.previous_move = position
        self.legal_moves = []
    def move(self, new_position):
        row_diff = abs(int(new_position[1]) - int(self.previous_move[1]))
        super().move(new_position)
        if row_diff == 2:
            self.just_moved_two = True  # Enable en passant possibility
        else:
            self.just_moved_two = False

    def promote(self, new_piece_type, positions):
        piece_classes = {'queen': Queen, 'rook': Rook, 'bishop': Bishop, 'knight': Knight}

        if new_piece_type not in piece_classes:
            print("Invalid piece type for promotion!")
            return False

        positions[self.position] = piece_classes[new_piece_type](self.color, self.position, self.status,self.previous_move)
        print()
        print(f"Pawn promoted to {new_piece_type.capitalize()} at {self.position}")
        return True

    def is_legal_move(self, new_position, positions):
        self.legal_moves.clear()
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])
        direction = 1 if self.color == 'white' else -1

        # Move by 1 square
        forward_one = f"{col}{row + direction}"
        if forward_one not in positions:
            self.legal_moves.append(forward_one)

        # Move by 2 squares, only from starting position
        if col == new_col and ((row == 2 and self.color == 'white' and new_row == 4) or (row == 7 and self.color == 'black' and new_row == 5)):
            intermediate_square = f"{col}{row + direction}"
            forward_two = f"{col}{row + 2 * direction}"
            if intermediate_square not in positions and forward_two not in positions:
                self.legal_moves.append(forward_two)

        # Capture move (excluding en passant)
        if abs(ord(col) - ord(new_col)) == 1 and new_row == row + direction:
            if new_position in positions and positions[new_position].color != self.color:
                capture_square = f"{new_position[0]}{new_position[1]}"
                self.legal_moves.append(capture_square)

        # En passant (latest chess update)
        if abs(ord(col) - ord(new_col)) == 1 and new_row == row + direction:
            adjacent_square = f"{new_col}{row}"
            if adjacent_square in positions:
                adjacent_piece = positions[adjacent_square]
                if isinstance(adjacent_piece, Pawn) and adjacent_piece.color != self.color and adjacent_piece.just_moved_two:
                    capture_square = f"{new_col}{new_row}"
                    self.legal_moves.append(capture_square)
        return new_position in self.legal_moves

class Rook(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('rook', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        if col == new_col or row == new_row:
            return self.is_path_clear(new_position, positions)
        return False

    def is_path_clear(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Vertical movement
        if col == new_col:
            step = 1 if new_row > row else -1
            for r in range(row + step, new_row, step):
                if f"{col}{r}" in positions:
                    return False

        # Horizontal movement
        elif row == new_row:
            step = 1 if ord(new_col) > ord(col) else -1
            for c in range(ord(col) + step, ord(new_col), step):  # Adjust range to not include the target square
                legal_square = f"{chr(c)}{row}"
                if legal_square in positions:
                    return False

        return new_position not in positions or positions[new_position].color != self.color


class Bishop(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('bishop', color, position, status, previous_move)
        self.legal_moves = []

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        if abs(ord(col) - ord(new_col)) == abs(row - new_row):
            return self.is_path_clear_diagonal(new_position, positions)
        else:
            return False

    def is_path_clear_diagonal(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Determine the step for columns and rows
        col_step = 1 if ord(new_col) > ord(col) else -1
        row_step = 1 if new_row > row else -1

        for i in range(1, abs(ord(new_col) - ord(col))):  # Exclude the target square
            check_col = chr(ord(col) + i * col_step)
            check_row = row + i * row_step
            check_square = f"{check_col}{check_row}"

            if check_square in positions:
                return False

        return new_position not in positions or positions[new_position].color != self.color


class Queen(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('queen', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        """Same methods used as in Bishop and Rook class, not super'ed for clarity"""
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Check if move is along the same column or row (Rook-like move)
        if col == new_col or row == new_row:
            return self.is_path_clear_straight(new_position, positions)

        # Check if move is along a diagonal (Bishop-like move)
        if abs(ord(col) - ord(new_col)) == abs(row - new_row):
            return self.is_path_clear_diagonal(new_position, positions)

        return False

    def is_path_clear_straight(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Vertical movement
        if col == new_col:
            step = 1 if new_row > row else -1
            for r in range(row + step, new_row, step):
                check_square = f"{col}{r}"
                if check_square in positions:  # Blocked by a piece
                    return False

        # Horizontal movement
        elif row == new_row:
            step = 1 if ord(new_col) > ord(col) else -1
            for c in range(ord(col) + step, ord(new_col), step):
                check_square = f"{chr(c)}{row}"
                if check_square in positions:  # Blocked by a piece
                    return False

        # If no blocks, return True
        return True

    def is_path_clear_diagonal(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Calculate movement steps
        col_step = 1 if ord(new_col) > ord(col) else -1
        row_step = 1 if new_row > row else -1

        # Check each square along the path
        for i in range(1, abs(ord(new_col) - ord(col))):  # Exclude the target square
            check_col = chr(ord(col) + i * col_step)
            check_row = row + i * row_step
            check_square = f"{check_col}{check_row}"

            if check_square in positions:
                return False

        return True

class King(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('king', color, position, status, previous_move)
        self.legal_moves = []

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Calculate the move's distance
        col_distance = abs(ord(col) - ord(new_col))
        row_distance = abs(row - new_row)

        if not (col_distance <= 1 and row_distance <= 1):
            return False

        if not ('a' <= new_col <= 'h' and 1 <= new_row <= 8):
            return False

        if new_position in positions and positions[new_position].color == self.color:
            return False

        return True

class Knight(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('knight', color, position, status, previous_move)
        self.legal_moves = []

    def is_legal_move(self, new_position, positions):
        self.legal_moves.clear()
        col, row = self.position[0], int(self.position[1])
        # Possible relative moves for a knight
        moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

        for change_col, change_row in moves:
            new_col = chr(ord(col) + change_col)
            new_row = row + change_row
            if 'a' <= new_col <= 'h' and 1 <= new_row <= 8:
                legal_square = f"{new_col}{new_row}"
                self.legal_moves.append(legal_square)

        return new_position in self.legal_moves

def create_chessboard_fancy():
    """Does what the name is."""
    rows = [8, 7, 6, 5, 4, 3, 2, 1]  # Row numbers
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Column labels

    chessboard_created = [[f"{col}{row}" for col in columns] for row in rows]

    return chessboard_created

def display_chessboard_fancy(board, pos):
    """Displays the chessboard with coloured squares and pieces"""
    column_labels = "   a  b  c  d  e  f  g  h"
    white_square = "\033[48;5;55m   \033[0m"
    black_square = "\033[48;5;22m   \033[0m"
    print(column_labels)

    for row_index, row in enumerate(board):
        line = f" {8 - row_index}"
        for col_index, square in enumerate(row):
            if square in pos:
                pieces = pos[square]
                if (row_index + col_index) % 2 == 0:
                    line += f"\033[48;5;55m {pieces} \033[0m"
                else:
                    line += f"\033[48;5;22m {pieces} \033[0m"
            else:
                if (row_index + col_index) % 2 == 0:
                    line += white_square
                else:
                    line += black_square
        print(line + f" {8 - row_index} ")
    print(column_labels)

# Create the chessboard
chessboard = create_chessboard_fancy()
# List of squares where the pawn can promote
promotion_squares = ["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"]
# Piece positions dictionary using class instances
pos = {
    # Black pieces
    'a8': Rook('black', 'a8'), 'b8': Knight('black', 'b8'), 'c8': Bishop('black', 'c8'), 'd8': Queen('black', 'd8'),
    'e8': King('black', 'e8'), 'f8': Bishop('black', 'f8'), 'g8': Knight('black', 'g8'), 'h8': Rook('black', 'h8'),
    'a7': Pawn('black', 'a7'), 'b7': Pawn('black', 'b7'), 'c7': Pawn('black', 'c7'), 'd7': Pawn('black', 'd7'),
    'e7': Pawn('black', 'e7'), 'f7': Pawn('black', 'f7'), 'g7': Pawn('black', 'g7'), 'h7': Pawn('black', 'h7'),

    # White pieces
    'a1': Rook('white', 'a1'), 'b1': Knight('white', 'b1'), 'c1': Bishop('white', 'c1'), 'd1': Queen('white', 'd1'),
    'e1': King('white', 'e1'), 'f1': Bishop('white', 'f1'), 'g1': Knight('white', 'g1'), 'h1': Rook('white', 'h1'),
    'a2': Pawn('white', 'a2'), 'b2': Pawn('white', 'b2'), 'c2': Pawn('white', 'c2'), 'd2': Pawn('white', 'd2'),
    'e2': Pawn('white', 'e2'), 'f2': Pawn('white', 'f2'), 'g2': Pawn('white', 'g2'), 'h2': Pawn('white', 'h2')
}
print()
print("Fancier chessboard to look at, was made in the first project and then scrapped, so i left it for art's sake")

# Displays a fancier looking chessboard at the beginning
display_chessboard_fancy(chessboard, pos)

print("Here go the player names!")
# Get the player name (not required)
playername1 = "" + input("Enter the first player's name: ")
playername2 = "" + input("Enter the second player's name: ")

if playername1 == "":
    playername1 = "anonymous"
if playername2 == "":
    playername2 = "anonymous"

# Creates a defaultdict for tracking the game state (instead of normal dict for handling empty keys)
board_state_tracker = defaultdict(int)

def saved_game_state(current_positions, isinplace):
    """Uses default dict to handle default values of missing a key, checks the amount of times a position has been reached."""
    state = tuple(sorted((key, piece.type, piece.color) for key, piece in current_positions.items()))
    if isinplace and isinplace != "help":
        board_state_tracker[state] += 1
    if isinplace == "help":
        messages.append(f"Threefold draw at : {board_state_tracker[state]}")
    if board_state_tracker[state] >= 3:
        messages.append("Threefold repetition detected! Game ends in a draw")
        time.sleep(2)
        exit()
    return {key: (piece.type, piece.color, piece.position, piece.status, piece.previous_move) for key, piece in current_positions.items()}

def restore_game_state(saved_state):
    """Restores the saved state of the board."""
    pos.clear()
    for key, value in saved_state.items():
        piece_type, color, position, status, previous_move = value
        if piece_type == 'pawn':
            pos[key] = Pawn(color, position, status, previous_move)
        elif piece_type == 'rook':
            pos[key] = Rook(color, position, status, previous_move)
        elif piece_type == 'knight':
            pos[key] = Knight(color, position, status, previous_move)
        elif piece_type == 'bishop':
            pos[key] = Bishop(color, position, status, previous_move)
        elif piece_type == 'queen':
            pos[key] = Queen(color, position, status, previous_move)
        elif piece_type == 'king':
            pos[key] = King(color, position, status, previous_move)

def castle_check(colour, choice):
    global current_color, enemy_color
    """Checks for a possibility of castling both ways for both sides, includes castling with check."""
    castled = False
    if choice == 'o-o':
        if colour == 'white':
            try:
                white_king = pos['e1']
                white_rook_h1 = pos['h1']
            except KeyError:
                messages.append("The king or the rook are not on their default positions")
                return False
            rook_moved = white_rook_h1 in pos.values() and white_rook_h1.previous_move == 'h1'
            king_moved = white_king in pos.values() and white_king.previous_move == 'e1'
            path_clear = all(square not in pos for square in ['f1', 'g1'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['e1','f1', 'g1'])
            if not rook_moved or not king_moved or not path_clear or not path_safe:
                messages.append("Castling impossible")
                return False
            else:
                white_king.move('g1')
                white_rook_h1.move('f1')
                pos['g1'] = white_king
                pos['f1'] = white_rook_h1
                del pos['e1']
                del pos['h1']
                castled = True

                enemy_king = [k for k, v in pos.items() if v.color == enemy_color and isinstance(v, King)][0]
                castled_with_check = is_square_attacked(enemy_king, enemy_color, pos)
                if castled_with_check:
                    messages.append("Roszada z szachem xD")

        elif colour == 'black':
            try:
                black_king = pos['e8']
                black_rook_h8 = pos['h8']
            except KeyError:
                messages.append("The king or the rook are not on their default positions")
                return False
            rook_moved = black_rook_h8 not in pos.values() or black_rook_h8.previous_move == 'h8'
            king_moved = black_king not in pos.values() or black_king.previous_move == 'e8'
            path_clear = all(square not in pos for square in ['f8', 'g8'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['e8', 'f8', 'g8'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                messages.append("Castling impossible")
                return False
            else:
                black_king.move('g8')
                black_rook_h8.move('f8')
                pos['g8'] = black_king
                pos['f8'] = black_rook_h8
                del pos['e8']
                del pos['h8']
                castled = True

                enemy_king = [k for k, v in pos.items() if v.color == enemy_color and isinstance(v, King)][0]
                castled_with_check = is_square_attacked(enemy_king, enemy_color, pos)
                if castled_with_check:
                    messages.append("Roszada z szachem xD")

    if choice == 'o-o-o':
        if colour == 'white':
            try:
                white_king = pos['e1']
                white_rook_a1 = pos['a1']
            except KeyError:
                messages.append("The king or the rook are not on their default positions")
                return False
            rook_moved = white_rook_a1 not in pos.values() or white_rook_a1.previous_move == 'a1'
            king_moved = white_king not in pos.values() or white_king.previous_move == 'h1'
            path_clear = all(square not in pos for square in ['b1', 'c1', 'd1'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['b1','c1','d1','e1'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                messages.append("Castling impossible")
                return False
            else:
                white_king.move('c1')
                white_rook_a1.move('d1')
                pos['c1'] = white_king
                pos['d1'] = white_rook_a1
                del pos['e1']
                del pos['a1']
                castled = True

                enemy_king = [k for k, v in pos.items() if v.color == enemy_color and isinstance(v, King)][0]
                castled_with_check = is_square_attacked(enemy_king, enemy_color, pos)
                if castled_with_check:
                    messages.append("Roszada z szachem xD")

        elif colour == 'black':
            try:
                black_king = pos['e8']
                black_rook_a8 = pos['a8']
            except KeyError:
                messages.append("The king or the rook are not on their default positions")
                return False
            rook_moved = black_rook_a8 not in pos.values() or black_rook_a8.previous_move == 'a8'
            king_moved = black_king not in pos.values() or black_king.previous_move == 'e8'
            path_clear = all(square not in pos for square in ['b8', 'c8', 'd8'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['b8', 'c8', 'd8', 'e8'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                messages.append("Castling impossible")
                return False
            else:
                black_king.move('c8')
                black_rook_a8.move('d8')
                pos['c8'] = black_king
                pos['d8'] = black_rook_a8
                del pos['e8']
                del pos['a8']
                castled = True

                enemy_king = [k for k, v in pos.items() if v.color == enemy_color and isinstance(v, King)][0]
                castled_with_check = is_square_attacked(enemy_king, enemy_color, pos)
                if castled_with_check:
                    messages.append("Roszada z szachem xD")
    if castled:
        return True
    return False

def is_square_attacked(square, color, positions):
    """Check if a square is attacked by any opponent piece. Also used as checking for checks (ironic)."""
    if square is None:
        return False
    for chess_piece in positions.values():
        if chess_piece.color != color:
            if chess_piece.is_legal_move(square, positions):
                return True
    return False

def simulate_move(piece, move_input, wanted_move):
    """Simulates a move to check for its legality, also checks for mate and checks."""
    saved_state = saved_game_state(pos, False)

    # Handle special flags for pawns
    just_moved_two_flag = None
    if isinstance(piece, Pawn):
        just_moved_two_flag = piece.just_moved_two

    # Simulate the move
    del pos[move_input]
    pos[wanted_move] = piece
    piece.position = wanted_move

    # Check if the move resolves the check
    king_position = wanted_move if isinstance(piece, King) else next((v.position for v in pos.values() if v.color == piece.color and isinstance(v, King)),None)
    in_check = is_square_attacked(king_position, piece.color, pos)

    # Restore the original state
    restore_game_state(saved_state)

    # Restore special flags for pawns
    if isinstance(piece, Pawn):
        piece.just_moved_two = just_moved_two_flag

    return not in_check

def checking():
    global current_color, enemy_color, messages
    """Checks if a move is a check (pun intended), also checks if a move doesn't leave your king in check."""
    saved_state = saved_game_state(pos, False)

    your_king = next((v.position for v in pos.values() if v.color == current_color and isinstance(v, King)), None)
    if is_square_attacked(your_king, current_color, pos):
        messages.append("Bro..., nice king you got there, you are in check")
        restore_game_state(saved_state)
        return False

    enemy_king = next((v.position for v in pos.values() if v.color == enemy_color and isinstance(v, King)), None)
    if is_square_attacked(enemy_king, enemy_color, pos):
        if is_checkmate(enemy_king, enemy_color, pos):
            time.sleep(2)
            messages.append("Checkmate!")
            exit()
        messages.append(f"Check on {enemy_king}")
    return True

def king_legal_moves(king, positions):
    """Returns a list of all legal moves for the king, More detailed that the is_legal_move in the King class, done like this to prevent
    problems with not returning a bool"""
    king_position = king.position
    legal_moves = []

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    col, row = king_position[0], int(king_position[1])

    for d_col, d_row in directions:
        new_col = chr(ord(col) + d_col)
        new_row = row + d_row
        target_square = f"{new_col}{new_row}"

        if 'a' <= new_col <= 'h' and 1 <= new_row <= 8:
            if king.is_legal_move(target_square, positions):
                if target_square not in positions or positions[target_square].color != king.color:
                    if simulate_move(king, king_position, target_square):
                        legal_moves.append(target_square)

    return legal_moves

def can_block_check(king_position, attacking_piece, positions):
    """Check if any piece can block the check or capture the attacking piece."""
    attacker_pos = attacking_piece.position
    attack_path = []
    # Find attack path using the attacker's movement rules
    if isinstance(attacking_piece, (Rook, Queen, Bishop)):
        current_pos = attacker_pos
        while current_pos != king_position:
            col_diff = ord(king_position[0]) - ord(current_pos[0])
            row_diff = int(king_position[1]) - int(current_pos[1])

            # Move step-wise towards the king
            step_col = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
            step_row = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)

            current_pos = f"{chr(ord(current_pos[0]) + step_col)}{int(current_pos[1]) + step_row}"
            if current_pos != king_position:  # Exclude the king's position itself
                attack_path.append(current_pos)

    # Pawns and Knights can't be blocked, only captured
    elif isinstance(attacking_piece, Knight):
        attack_path = [attacker_pos]

    elif isinstance(attacking_piece, Pawn):
        attack_path = [attacker_pos]

    # Check if any piece can block or capture the attacker, dict copy to avoid overwritting during move simulation
    for position, piece in positions.copy().items():
        if piece.color == attacking_piece.color:
            continue

        # Special case: Check if the king can capture the attacker directly
        if piece.type == 'king':
            if simulate_move(piece, position, attacker_pos) and piece.is_legal_move(position, attacker_pos):
                messages.append(f"King captures the attacker at {attacker_pos}")
                return True

        # Special case: Piece is directly near the king
            if not attack_path:
                if piece.is_legal_move(attacker_pos, positions):
                    if simulate_move(piece, position, attacker_pos):
                        return True

        # Normal case, trying to block the check or take the piece
        else:
            for square in attack_path:
                if piece.color != attacking_piece.color:
                    if piece.is_legal_move(square, positions):
                        if simulate_move(piece, position, square) or simulate_move(piece, position, attacker_pos):
                            messages.append(f"Game goes on, {piece.type.capitalize()}, {piece.color} at {square}")
                            return True
                    if piece.is_legal_move(attacker_pos, positions):
                        if simulate_move(piece, position, attacker_pos):
                            messages.append(f"Game goes on, {piece.type.capitalize()} can take the attacker at {attacker_pos}")
                            return True
    return False

def is_checkmate(king_position, king_color, positions):
    global messages
    """Checks if a move is mate, ends the game if so."""
    not_in_check = False
    king = positions[king_position]
    if not is_square_attacked(king_position, king_color, positions):
        not_in_check = True
    legal_moves = king_legal_moves(king,positions)
    if legal_moves:
        messages.append(f"Game goes on, King can move to {legal_moves}")
        return False
    for attacker_pos, attacker in positions.items():
        if attacker.color != king_color and attacker.is_legal_move(king_position, positions):
            if can_block_check(king_position, attacker, positions):
                return False
    if not not_in_check:
        messages.append("Checkmate!")
        return True
    elif not legal_moves_check(pos):
        messages.append("It's Stalemate, game over!")
        return True

def count_pieces(positions):
    """Does what the name is."""
    counter = Counter(piece.type for piece in positions.values())
    return counter

fifty_move_check = 0
last_moved_pawn = None

def moving(piece, move_input, wanted_move, messages):
    """Main function for moving pieces, also checks for 50 move draw and en passant possibility."""
    global fifty_move_check, last_moved_pawn, move_counter
    #Checks for en passant possibility
    if isinstance(piece, Pawn) and last_moved_pawn is not None:
        if last_moved_pawn.just_moved_two:
            target_row = int(piece.position[1]) + (1 if piece.color == 'white' else -1)
            true_row = int(piece.position[1])
            target_square = f"{wanted_move[0]}{target_row}"
            true_square = f"{wanted_move[0]}{true_row}"
            if abs(ord(piece.position[0]) - ord(wanted_move[0])) == 1:
                if target_square not in pos and (abs(ord(piece.position[0]) - ord(last_moved_pawn.position[0])) == 1) and (piece.position[1] == last_moved_pawn.position[1]):
                    if not simulate_move(piece, move_input, wanted_move):
                        messages.append("Illegal move, doesn't block the check")
                        return False
                    del pos[true_square]
                    piece.move(wanted_move)
                    pos[wanted_move] = piece
                    del pos[move_input]
                    is_viable = checking()
                    if not is_viable:
                        return False
                    piece.just_moved_two = False
                    fifty_move_check = 0
                    move_counter += 1
                    saved_game_state(pos, True)
                    return True

    # Normal move without any captures
    if piece.is_legal_move(wanted_move, pos):
        if wanted_move not in pos:
            if not simulate_move(piece, move_input, wanted_move):
                messages.append("Illegal move, doesn't block the check")
                return False

            piece.move(wanted_move)
            pos[wanted_move] = piece
            del pos[move_input]

            is_viable = checking()
            if not is_viable:
                return False

            if isinstance(piece, Pawn) and wanted_move in promotion_squares:
                valid_pieces = ['queen', 'rook', 'bishop', 'knight']
                new_piece = 'queen'
                while new_piece not in valid_pieces:
                    new_piece = input("Promote pawn to (queen, rook, bishop, knight): ").lower()
                piece.promote(new_piece, pos)

            if isinstance(piece, Pawn) and move_counter != 1:
                last_moved_pawn = piece
                fifty_move_check = 0
            else:
                fifty_move_check += 1

            if fifty_move_check >= 50:
                messages.append("Draw by 50 move rule!")
                exit()
            move_counter += 1
            saved_game_state(pos, True)
            return True

        # A move including the capture
        else:
            target = pos[wanted_move]
            if target.color != piece.color:
                if not simulate_move(piece, move_input, wanted_move):
                    messages.append("Illegal move, doesn't block the check")
                    return False
                piece.move(wanted_move)
                pos[wanted_move] = piece
                del pos[move_input]
                target.status = False

                is_viable = checking()
                if not is_viable:
                    target.status = True
                    return False

                counter = count_pieces(pos)
                if len(pos) == 3:
                    if 'bishop' in counter or 'knight' in counter:
                        messages.append("Insufficient checkmate material, game ends in a draw!")
                        exit()

                if len(pos) == 4 and counter['bishop'] == 2:
                    bishops = [pieces for pieces in pos.values() if pieces.type == 'bishop']
                    colors = [(ord(b.position[0]) + int(b.position[1])) % 2 for b in bishops]
                    if colors[0] == colors[1]:
                        messages.append("Insufficient checkmate material, game ends in a draw!")
                        exit()

                if all(isinstance(piece, King) for piece in pos.values()):
                    messages.append("Draw by force, only kings remain!")
                    exit()

                if isinstance(piece, Pawn) and wanted_move in promotion_squares:
                    valid_pieces = ['queen', 'rook', 'bishop', 'knight']
                    new_piece = 'queen'
                    while new_piece not in valid_pieces:
                        new_piece = input("Promote pawn to (queen, rook, bishop, knight): ").lower()
                    piece.promote(new_piece, pos)
                fifty_move_check = 0

                move_counter += 1
                saved_game_state(pos, True)
                return True
            else:
                messages.append("Illegal move, a piece is on the way")
                return False
    else:
        messages.append("Illegal move")
        return False

def legal_moves_check(positions):
    """Checks for legality of all moves to help with stalemate checks"""
    legal_moves_list = []
    for position, piece in positions.items():
        for col in 'abcdefgh':
            for row in '12345678':
                target_square = f"{col}{row}"
                if piece.is_legal_move(target_square, position) and simulate_move(piece, position, target_square):
                    legal_moves_list.append(target_square)
    if not legal_moves_list:
        return False
    return True

def get_current_player():
    """It really cannot get any more simple than that."""
    return playername1 if current_color == 'white' else playername2

first = True
game = True
move_counter = 0
current_color = 'white'
enemy_color = 'black'
current_player = playername1
enemy_player = playername2

def game_loop(stdscr):
    """Main game loop, includes curses and different displaying of the board (not so pretty :c)"""
    global messages
    global current_color, enemy_color, move_counter, fifty_move_check, board_state_tracker, current_player, enemy_player
    def initialize_colors():
        """Does what the name is"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default color
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Black text on white (for white squares)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White text on black (for black squares)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Greenish glowing edges
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)  # Red highlight for check
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN) # Black text on cyan
    initialize_colors()

    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)
    stdscr.keypad(True)

    # Starting position for the selector
    selector_row, selector_col = 0, 0

    def highlight_square(stdscr, row, col, label, is_piece):
        """Highlight the current square on the chessboard."""
        y, x = row + 1, col * 4 + 2  # Adjust coordinates for curses, can be changed when the board size is changed

        color = curses.color_pair(6)

        if is_piece:
            stdscr.addstr(y, x - 1, f"[{label} ]", curses.A_BOLD | color)
        else:
            stdscr.addstr(y, x - 1, f" {label} ", color)

    def display_chessboard_with_selector(stdscr, chessboard, pos, selected_row, selected_col, messages=None):
        """Display the chessboard with the currently selected square highlighted."""
        column_labels = "  a   b   c   d   e   f   g   h"

        king_in_check = None
        for square, piece in pos.items():
            if isinstance(piece, King) and is_square_attacked(square, piece.color, pos):
                king_in_check = square
                break

        stdscr.addstr(0, 0, column_labels)

        for row_index, row in enumerate(chessboard):
            line = f" {8 - row_index} "
            for col_index, square in enumerate(row):
                piece = pos.get(square, " ")
                is_piece = piece != " "
                label = str(piece) if is_piece else f"  "

                is_white_square = (row_index + col_index) % 2 == 0
                color = curses.color_pair(2) if is_white_square else curses.color_pair(3)

                if square == king_in_check:
                    color = curses.color_pair(7)
                if row_index == selected_row and col_index == selected_col:
                    highlight_square(stdscr, row_index, col_index, label, is_piece)
                else:
                    y, x = row_index+ 1, col_index * 4 + 2  # Adjust for curses grid, depending on terminal size
                    stdscr.addstr(y, x - 1, f" {label:<3}", color)

            stdscr.addstr(row_index + 1, len(line) + len(row) * 4, f"{8 - row_index}")

        stdscr.addstr(len(chessboard) + 1, 0, column_labels)

        control_start_x = len(chessboard[0]) * 10 + 6  # Place for controls, can also be changed
        control_start_y = 0

        # Render the control section
        controls = [
            "Controls:",
            "Arrow Keys: Move selector",
            "'s': Select/move piece",
            "'q': Quit game",
            "'r': Reset input",
            "'d': Short castle (o-o)",
            "'a': Long castle (o-o-o)",
            "'h': Show help (draw counters)",
            "'v': Draw by agreement (has to be clicked by both players)",
            f"Move counter: {move_counter} (for each player, when considering a fifty move draw this number is halfed)"
        ]

        for i, control in enumerate(controls):
            if "Move counter" in control:  # Special color for fun
                stdscr.addstr(control_start_y + i, control_start_x, control, curses.color_pair(8))
            else:  # Default rendering
                stdscr.addstr(control_start_y + i, control_start_x, control)

        message_start_y = len(chessboard) + 3
        max_message_rows = 10 # Can be changed, but can easily crash if given too big numbers
        if messages:
            truncated_messages = messages[-max_message_rows:] # Slices the messages to not overflow the output
            for i in range(max_message_rows):
                stdscr.move(message_start_y + i, 0)
                stdscr.clrtoeol()

            for i, message in enumerate(truncated_messages):
                stdscr.addstr(message_start_y + i, 0, message)

        stdscr.refresh()

    move_input = None
    game_running = True
    correct_move = False
    drawer = False
    white_drawer = False
    black_drawer = False

    # Display the initial board and messages
    messages.append(f"{playername1.capitalize()} vs {playername2.capitalize()}, look to the right for controls if you didn't notice them already")
    messages.append(f"Game made by me (K.M), enjoy!")
    display_chessboard_with_selector(stdscr, chessboard, pos, selector_row, selector_col, messages)
    messages.clear()

    while game_running:
        while not correct_move:
            key = stdscr.getch()
            if key != -1:  # Only handle non-idle keys
                if key == curses.KEY_UP and selector_row > 0:
                    selector_row -= 1
                elif key == curses.KEY_DOWN and selector_row < 7:
                    selector_row += 1
                elif key == curses.KEY_LEFT and selector_col > 0:
                    selector_col -= 1
                elif key == curses.KEY_RIGHT and selector_col < 7:
                    selector_col += 1
                elif key == ord('s'):  # Can be changed to any key, just for moving
                    selected_square = chessboard[selector_row][selector_col]
                    if move_input is None:
                        move_input = selected_square
                        if selected_square in pos:
                            messages.append(f"Selected piece: {move_input}")
                        else:
                            messages.append("Empty square selected, choose a piece")
                            move_input = None
                    else:
                        wanted_move = selected_square
                        if wanted_move not in pos.items():
                            messages.append(f"Moving {move_input} to {wanted_move}")
                            piece = pos.get(move_input)
                            if piece and piece.color == current_color:
                                if moving(piece, move_input, wanted_move, messages):
                                    correct_move = False
                                    move_input = None
                                    current_color, enemy_color, current_player = enemy_color, current_color, enemy_player
                                    messages.append(f"{current_color.capitalize()}'s turn, player {get_current_player().capitalize()} to move")
                            else:
                                messages.append("Invalid selection or move!")
                                move_input = None
                elif key == ord('q'):  # Quit the game, key can also be changed
                    messages = ["Quitting the game!"]
                    display_chessboard_with_selector(stdscr, chessboard, pos, selector_row, selector_col, messages)
                    stdscr.refresh()
                    time.sleep(2)
                    game_running = False
                    correct_move = True
                    break
                elif key == ord('r'): # Resetting the input
                    messages = [f"The input is reset, previous input was {move_input}"]
                    move_input = None
                elif key == ord('d'): # Castling short side
                    messages = [f"Trying to castle short side for {current_color}"]
                    if castle_check(current_color, 'o-o'):
                        move_input = None
                        current_color, enemy_color, current_player = enemy_color, current_color, enemy_player
                        messages.append("Castling done")
                        messages.append(f"{current_color.capitalize()}'s turn, player {get_current_player().capitalize()} to move")
                elif key == ord('a'): # Castling long side
                    messages = [f"Trying to castle long side for {current_color}"]
                    if castle_check(current_color, 'o-o-o'):
                        move_input = None
                        current_color, enemy_color, current_player = enemy_color, current_color, enemy_player
                        messages.append("Castling done")
                        messages.append(f"{current_color.capitalize()}'s turn, player {get_current_player().capitalize()} to move")
                elif key == ord('v'): # Draw by agreement
                    if current_color == 'white' and drawer == False:
                        white_drawer = True
                        messages.append(f"{get_current_player().capitalize()} sends a draw offer")
                    if current_color == 'black' and drawer == False:
                        black_drawer = True
                        messages.append(f"{get_current_player().capitalize()} sends a draw offer")
                    if white_drawer and black_drawer:
                        messages = ["Draw by agreement!"]
                        display_chessboard_with_selector(stdscr, chessboard, pos, selector_row, selector_col, messages)
                        stdscr.refresh()
                        time.sleep(2)
                        game_running = False
                        correct_move = True
                        break
                elif key == ord('h'): # Helper, displays some info about draws
                    messages.append(f"If you can't play chess, here it is: https://www.chess.com/terms/chess-pieces")
                    messages.append(f"Draw offers by white and black: {white_drawer}, {black_drawer}")
                    messages.append(f"Fifty move draw at : {fifty_move_check}")
                    saved_game_state(pos, "help")
                if len(messages) > 13:
                    messages = []

                display_chessboard_with_selector(stdscr, chessboard, pos, selector_row, selector_col, messages)

curses.wrapper(game_loop)








#Dodane linijki zeby bylo ladnie rowno 1000 :)