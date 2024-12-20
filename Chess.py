
from collections import defaultdict, Counter


class Piece:
    def __init__(self, type, color, position, status=True, previous_move=None):
        self.type = type
        self.color = color
        self.position = position
        self.status = status
        self.previous_move = previous_move

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

    def move(self, new_position):
        self.previous_move = self.position
        self.position = new_position

        # Check if this move was a two-square move
        if abs(int(new_position[1]) - int(self.previous_move[1])) == 2:
            self.just_moved_two = True  # Enable en passant possibility
        else:
            self.just_moved_two = False  # Reset flag otherwise

    def promote(self, new_piece_type, positions):
        """Promote the pawn to another piece."""
        # List of valid promotion pieces
        piece_classes = {'queen': Queen, 'rook': Rook, 'bishop': Bishop, 'knight': Knight}

        if new_piece_type not in piece_classes:
            print("Invalid piece type for promotion!")
            return False

        # Replace pawn with the chosen piece
        positions[self.position] = piece_classes[new_piece_type](self.color, self.position, self.status,self.previous_move)
        print(f"Pawn promoted to {new_piece_type.capitalize()} at {self.position}")
        return True


    def is_legal_move(self, new_position, positions):
        # Current position
        col, row = self.position[0], int(self.position[1])
        # New position
        new_col, new_row = new_position[0], int(new_position[1])
        # Movement direction based on color
        direction = 1 if self.color == 'white' else -1

        # --- Forward Move (1 square) ---
        if col == new_col and new_row == row + direction:
            if new_position not in positions:  # Square must be empty
                return True

        # --- Double Move (2 squares from starting position) ---
        if col == new_col and ((row == 2 and self.color == 'white' and new_row == 4) or (row == 7 and self.color == 'black' and new_row == 5)):
            intermediate_square = f"{col}{row + direction}"
            if new_row == row + 2 * direction:  # Move two squares forward
                if intermediate_square not in positions and new_position not in positions:  # Path must be clear
                    return True

        # --- Capture Move (Diagonal Move) ---
        if abs(ord(col) - ord(new_col)) == 1 and new_row == row + direction:  # Move diagonally
            if new_position in positions and positions[new_position].color != self.color:  # Opponent's piece
                return True

        # --- En passant (latest chess update) ---

        if abs(ord(col) - ord(new_col)) == 1 and new_row == row + direction:  # Diagonal move
            adjacent_square = f"{new_col}{row}"  # Square where the opponent pawn is
            if adjacent_square in positions:  # Check if there's a pawn there
                adjacent_piece = positions[adjacent_square]
                if isinstance(adjacent_piece,Pawn) and adjacent_piece.color != self.color and adjacent_piece.just_moved_two:
                    return True

        # --- Invalid Move ---
        return False

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

        if col == new_col:
            step = 1 if new_row > row else -1
            for r in range(row + step, new_row, step):
                if f"{col}{r}" in positions:
                    return False
        elif row == new_row:
            step = 1 if ord(new_col) > ord(col) else -1
            for c in range(ord(col) + step, ord(new_col), step):
                if f"{chr(c)}{row}" in positions:
                    return False
        return True

class Bishop(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('bishop', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        if abs(ord(col) - ord(new_col)) == abs(row - new_row):
            return self.is_path_clear_diagonal(new_position, positions)
        return False

    def is_path_clear_diagonal(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        col_step = 1 if ord(new_col) > ord(col) else -1
        row_step = 1 if new_row > row else -1

        for i in range(1, abs(ord(new_col) - ord(col))):
            check_col = chr(ord(col) + i * col_step)
            check_row = row + i * row_step
            if f"{check_col}{check_row}" in positions:
                return False
        return True

class Queen(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('queen', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        # Current position
        col, row = self.position[0], int(self.position[1])
        # New position
        new_col, new_row = new_position[0], int(new_position[1])

        # Check if move is along the same column or row (Rook-like move)
        if col == new_col or row == new_row:
            return self.is_path_clear_straight(new_position, positions)

        # Check if move is along a diagonal (Bishop-like move)
        if abs(ord(col) - ord(new_col)) == abs(row - new_row):
            return self.is_path_clear_diagonal(new_position, positions)

        # If it's neither a straight nor a diagonal move, it's invalid
        return False

    def is_path_clear_straight(self, new_position, positions):
        """Check if path is clear for straight moves (row or column)."""
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Moving vertically (same column)
        if col == new_col:
            step = 1 if new_row > row else -1
            for r in range(row + step, new_row, step):
                if f"{col}{r}" in positions:  # Blocked by a piece
                    return False

        # Moving horizontally (same row)
        elif row == new_row:
            step = 1 if ord(new_col) > ord(col) else -1
            for c in range(ord(col) + step, ord(new_col), step):
                if f"{chr(c)}{row}" in positions:  # Blocked by a piece
                    return False

        return True

    def is_path_clear_diagonal(self, new_position, positions):
        """Check if path is clear for diagonal moves."""
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])

        # Calculate movement steps
        col_step = 1 if ord(new_col) > ord(col) else -1
        row_step = 1 if new_row > row else -1

        # Check each square along the diagonal path
        for i in range(1, abs(ord(new_col) - ord(col))):
            check_col = chr(ord(col) + i * col_step)
            check_row = row + i * row_step
            if f"{check_col}{check_row}" in positions:  # Blocked by a piece
                return False

        return True

class King(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('king', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])
        return max(abs(ord(col) - ord(new_col)), abs(row - new_row)) == 1

class Knight(Piece):
    def __init__(self, color, position, status=True, previous_move=None):
        super().__init__('knight', color, position, status, previous_move)

    def is_legal_move(self, new_position, positions):
        col, row = self.position[0], int(self.position[1])
        new_col, new_row = new_position[0], int(new_position[1])
        return (abs(ord(col) - ord(new_col)), abs(row - new_row)) in [(1, 2), (2, 1)]


def create_chessboard():
    rows = [8, 7, 6, 5, 4, 3, 2, 1]  # Row numbers
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # Column labels

    chessboard_created = [[f"{col}{row}" for col in columns] for row in rows]

    return chessboard_created

def display_chessboard(board, pos):
    column_labels = "  a  b  c  d  e  f  g  h"
    white_square = "\033[47m   \033[0m"  # White square
    black_square = "   "  # Black square

    print(column_labels)
    for row_index, row in enumerate(board):
        line = f"{8 - row_index} "  # Add row number at the beginning of the line
        for col_index, square in enumerate(row):
            if square in pos:  # Check if there's a piece on the square
                pieces = pos[square]
                # Display the piece on the correct color square
                if (row_index + col_index) % 2 == 0:
                    line += f"\033[47m {pieces} \033[0m"
                else:
                    line += f" {pieces} "
            else:  # Empty square
                if (row_index + col_index) % 2 == 0:
                    line += white_square
                else:
                    line += black_square
        print(line + f" {8 - row_index}")  # Add row number at the end of the line
    print(column_labels)

# Create the chessboard
chessboard = create_chessboard()
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


# Display the chessboard with pieces
display_chessboard(chessboard, pos)

def playersign(pmove):
    return not pmove

playername1 = input("Podaj nazwę pierwszego gracza: ")
playername2 = input("Podaj nazwę drugiego gracza: ")

board_state_tracker = defaultdict(int)

def saved_game_state(current_positions):
    """Uses default dict to handle default values of missing a key, checks the amount of times a position has been reached"""
    state = tuple(sorted((key, piece.type, piece.color) for key, piece in current_positions.items()))
    board_state_tracker[state] += 1
    if board_state_tracker[state] >= 450000:
        print("Threefold repetition detected! Game ends in a draw")
        exit()
    return {key: (piece.type, piece.color, piece.position, piece.status, piece.previous_move) for key, piece in current_positions.items()}

def restore_game_state(saved_state):
    """Restore the saved state of the board."""
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
    castled = False
    if choice == 'O-O':
        if colour == 'white':
            white_king = pos['e1']
            white_rook_h1 = pos['h1']
            rook_moved = white_rook_h1 not in pos or white_rook_h1.previous_move is not None
            king_moved = white_king not in pos or white_king.previous_move is not None
            path_clear = all(square not in pos for square in ['f1', 'g1'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['e1','f1', 'g1'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                print("Roszada niemożliwa")
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
                    print("Roszada z szachem xD")

        elif colour == 'black':
            black_king = pos['e8']
            black_rook_h8 = pos['h8']
            rook_moved = black_rook_h8 not in pos or black_rook_h8.previous_move is not None
            king_moved = black_king not in pos or black_king.previous_move is not None
            path_clear = all(square not in pos for square in ['f8', 'g8'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['e8', 'f8', 'g8'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                print("Roszada niemożliwa")
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
                    print("Roszada z szachem xD")

    if choice == 'O-O-O':
        if colour == 'white':
            white_king = pos['e1']
            white_rook_a1 = pos['a1']
            rook_moved = white_rook_a1 not in pos or white_rook_a1.previous_move is not None
            king_moved = white_king not in pos or white_king.previous_move is not None
            path_clear = all(square not in pos for square in ['b1', 'c1', 'd1'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['b1','c1','d1','e1'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                print("Roszada niemożliwa")
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
                    print("Roszada z szachem xD")

        elif colour == 'black':
            black_king = pos['e8']
            black_rook_a8 = pos['a8']
            rook_moved = black_rook_a8 not in pos or black_rook_a8.previous_move is not None
            king_moved = black_king not in pos or black_king.previous_move is not None
            path_clear = all(square not in pos for square in ['b8', 'c8', 'd8'])
            path_safe = all(not is_square_attacked(square, colour, pos) for square in ['b8', 'c8', 'd8', 'e8'])

            if rook_moved or king_moved or not path_clear or not path_safe:
                print("Roszada niemożliwa")
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
                    print("Roszada z szachem xD")
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
    # Save the current state
    saved_state = saved_game_state(pos)

    just_moved_two_flag = None
    if isinstance(piece, Pawn):
        just_moved_two_flag = piece.just_moved_two

    your_king = next((v.position for v in pos.values() if v.color == piece.color and isinstance(v, King)), None)

    # Ensure we simulate a king move safely without affecting checks
    simulated_king_pos = wanted_move if isinstance(piece, King) else your_king
    # Simulate the move
    pos[wanted_move] = piece
    del pos[move_input]
    piece.position = wanted_move
    # Check if the king is in check after this move
    in_check = is_square_attacked(simulated_king_pos, current_color, pos)
    # Checks if the move was winning
    checking()
    # Restore the original state
    restore_game_state(saved_state)

    if isinstance(piece, Pawn):
        piece.just_moved_two = just_moved_two_flag

    # Return True if the move doesn't leave the king in check
    return not in_check

def checking():
    saved_state = saved_game_state(pos)

    your_king = next((v.position for v in pos.values() if v.color == current_color and isinstance(v, King)), None)
    if is_square_attacked(your_king, current_color, pos):
        print("Bro..., nice king you got there")
        restore_game_state(saved_state)
        return False
    # Finalize move if valid
    enemy_king = next((v.position for v in pos.values() if v.color == enemy_color and isinstance(v, King)), None)
    if is_square_attacked(enemy_king, enemy_color, pos):
        if is_checkmate(enemy_king, enemy_color, pos):
            print("Szach mat!")
            display_chessboard(chessboard, pos)
            exit()
        print(f"Szach króla na {enemy_king}")
    return True

def king_legal_moves(king, positions):
    """Returns a list of all legal moves for the king using its class method."""
    legal_moves = []
    # Loop through all squares on the board to find valid moves
    for col in 'abcdefgh':
        for row in '12345678':
            target_square = f"{col}{row}"

            if king.is_legal_move(target_square, positions):
                if target_square not in positions or positions[target_square].color != king.color:
                    if not is_square_attacked(target_square, king.color, positions):
                        legal_moves.append(target_square)

    return legal_moves

def can_block_check(king_position, attacking_piece, positions):
    """
    Check if any piece can block the check or capture the attacking piece.
    """
    # Get attacker's position
    attacker_pos = attacking_piece.position
    attack_path = []

    # Find attack path using the attacker's movement rules
    if isinstance(attacking_piece, (Rook, Queen, Bishop)):
        # Check if the attacker has a linear path
        current_pos = attacker_pos
        while current_pos != king_position:
            col_diff = ord(king_position[0]) - ord(current_pos[0])
            row_diff = int(king_position[1]) - int(current_pos[1])

            # Move step-wise towards the king
            step_col = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
            step_row = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)

            # Generate the next square in the path
            current_pos = f"{chr(ord(current_pos[0]) + step_col)}{int(current_pos[1]) + step_row}"
            if current_pos != king_position:  # Exclude the king's position itself
                attack_path.append(current_pos)

    elif isinstance(attacking_piece, Knight):
        # Knights can't be blocked; only capturing is valid
        attack_path = [attacker_pos]

    elif isinstance(attacking_piece, Pawn):
        # Pawns can't be blocked; only capturing is valid
        attack_path = [attacker_pos]

    # Check if any piece can block or capture the attacker
    for position, piece in positions.items():
        if piece.color != attacking_piece.color or piece.type == 'king':  # Only check friendly pieces
            continue
        for square in attack_path:
            if piece.is_legal_move(square, positions):
                if piece.type == 'king':
                    continue
                # Simulate the move to verify it doesn't leave the king in check
                if simulate_move(piece, position, square):
                    print(f"Game goes on, {piece.type.capitalize()} at {square}")
                    return True

    return False

def is_checkmate(king_position, king_color, positions):
    king = positions[king_position]
    if not is_square_attacked(king_position, king_color, positions):
        return False

    legal_moves = king_legal_moves(king,positions)

    if legal_moves:
        print(f"Legalne ruchy w {legal_moves}")
        return False

    for attacker_pos, attacker in positions.items():
        if attacker.color != king_color and attacker.is_legal_move(king_position, positions):
            if can_block_check(king_position, attacker, positions):
                return False

        # If no escape moves or blocks, it's checkmate
    return True

def count_pieces(positions):
    counter = Counter(piece.type for piece in positions.values())
    return counter

fifty_move_check = 0
last_moved_pawn = None
def moving(piece, move_input, wanted_move, move_counter):
    global fifty_move_check
    global last_moved_pawn
    if isinstance(piece, Pawn) and last_moved_pawn is not None:
        if last_moved_pawn.just_moved_two:
            target_row = int(piece.position[1]) + (1 if piece.color == 'white' else -1)
            true_row = int(piece.position[1])
            target_square = f"{wanted_move[0]}{target_row}"
            true_square = f"{wanted_move[0]}{true_row}"
            if abs(ord(piece.position[0]) - ord(wanted_move[0])) == 1:
                if target_square not in pos and (abs(ord(piece.position[0]) - ord(last_moved_pawn.position[0])) == 1) and (piece.position[1] == last_moved_pawn.position[1]):
                    if not simulate_move(piece, move_input, wanted_move):
                        print("Nielegalny ruch, nie blokuje szacha")
                        return False
                    del pos[true_square]  # Remove captured pawn
                    piece.move(wanted_move)  # Move capturing pawn
                    pos[wanted_move] = piece
                    del pos[move_input]  # Remove the original position
                    is_viable = checking()
                    if not is_viable:
                        return False
                    piece.just_moved_two = False
                    fifty_move_check = 0
                    return True

    if piece.is_legal_move(wanted_move, pos):
        if wanted_move not in pos:
            if not simulate_move(piece, move_input, wanted_move):
                print("Nielegalny ruch, nie blokuje szacha")
                return False


            piece.move(wanted_move)
            pos[wanted_move] = piece
            del pos[move_input]

            is_viable = checking()
            if not is_viable:
                return False

            if isinstance(piece, Pawn) and wanted_move in promotion_squares:
                valid_pieces = ['queen', 'rook', 'bishop', 'knight']
                new_piece = ''
                while new_piece not in valid_pieces:
                    new_piece = input("Promote pawn to (queen, rook, bishop, knight): ").lower()
                piece.promote(new_piece, pos)

            if isinstance(piece, Pawn) and move_counter != 1:
                last_moved_pawn = piece
                print(last_moved_pawn)
                print(last_moved_pawn.just_moved_two)
                fifty_move_check = 0
            else:
                fifty_move_check += 1

            if fifty_move_check >= 50:
                print("Draw by 50 move rule!")
                exit()

            return True
        else:
            target = pos[wanted_move]
            if target.color != piece.color:
                if not simulate_move(piece, move_input, wanted_move):
                    print("Nielegalny ruch, nie blokuje szacha")
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
                        print("Insufficent checkmate material, game ends in a draw!")
                        exit()

                if len(pos) == 4 and counter['bishop'] == 2:
                    bishops = [pieces for pieces in pos.values() if pieces.type == 'bishop']
                    colors = [(ord(b.position[0]) + int(b.position[1])) % 2 for b in bishops]
                    if colors[0] == colors[1]:
                        print("Insufficent checkmate material, game ends in a draw!")
                        exit()
                if all(isinstance(piece, King) for pieces in pos.values()):
                    print("Draw by force, only kings remain!")
                    exit()

                if isinstance(piece, Pawn) and wanted_move in promotion_squares:
                    valid_pieces = ['queen', 'rook', 'bishop', 'knight']
                    new_piece = ''
                    while new_piece not in valid_pieces:
                        new_piece = input("Promote pawn to (queen, rook, bishop, knight): ").lower()
                    piece.promote(new_piece, pos)
                fifty_move_check = 0

                return True
            else:
                print("Nielegalny ruch - własna figura na celu")
                return False
    else:
        print("Nielegalny ruch")
        return False

def validate_input(prompt):
    while True:  # Keep asking until valid input is provided
        try:
            move_inputted = input(prompt).strip().lower()  # Get input and normalize to lowercase

            # Check length (must be exactly 2 characters)
            if len(move_inputted) != 2:
                raise ValueError("Invalid input length. Must be 2 characters (e.g., 'a1').")

            # Check if the first character is a valid column (a-h)
            column = move_inputted[0]
            if column < 'a' or column > 'h':
                raise ValueError("Invalid column. Must be between 'a' and 'h'.")

            # Check if the second character is a valid row (1-8)
            row = move_inputted[1]
            if row < '1' or row > '8':
                raise ValueError("Invalid row. Must be between '1' and '8'.")

            # If all checks pass, return the valid input
            return move_inputted

        except ValueError as e:
            print(f"Invalid input: {e}")
            print("Please enter a valid position between 'a1' and 'h8'.")

first = True
playermove = True
game = True
move_counter = 0
while game:
    move_counter += 1
    if first:
        print(f"Teraz nastąpi ruch gracza {playername1}")
        current_color = 'white'
        enemy_color = 'black'
    else:
        print(f"Teraz nastąpi ruch gracza {playername2}")
        current_color = 'black'
        enemy_color = 'white'
    if move_counter >= 40:
        draw_agreement = input("Agree to a draw? (Y/N): ").lower()
        if draw_agreement == 'y':
            print("Game ends in a draw by agreement!")

    correctmove = False

    while not correctmove:
        move_input = validate_input("Podaj pole figury którą chcesz ruszyć: ")
        has_castled = castle_check(current_color, move_input)
        if has_castled:
            correctmove = True
            break
        if move_input in pos:
            piece = pos[move_input]
            if piece.color == current_color:
                wanted_move = input('Podaj pole na które chcesz się ruszyć: ').strip().lower()
                move_done = moving(piece, move_input, wanted_move, move_counter)
                if move_done:
                    correctmove = True
            else:
                print("Nie możesz ruszać figurami przeciwnika")
        else:
            print("Wybrałeś pole bez figury")

    display_chessboard(chessboard, pos)

    if False:
        pass
    else:
        for p in pos.values():
            if isinstance(p, Pawn):
                p.just_moved_two = False
        if last_moved_pawn:
            last_moved_pawn.just_moved_two = True
        first = playersign(first)