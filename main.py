import chess
import random


def allows_mate_in_one(move, board):
    board.push(move)
    opponent_can_mate = False

    for opp_move in board.legal_moves:
        board.push(opp_move)
        if board.is_checkmate():
            opponent_can_mate = True
            board.pop()
            break
        board.pop()

    board.pop()
    return opponent_can_mate


def leaves_takeable_piece(move, board):
    board.push(move)
    is_takeable = False

    # After the move, for each of our pieces
    for square, piece in board.piece_map().items():
        if piece.color != board.turn or piece.piece_type == chess.PAWN:
            continue  # Skip enemy pieces

        attackers = board.attackers(not board.turn, square)
        defenders = board.attackers(board.turn, square)

        if len(attackers) > len(defenders):
            is_takeable = True
            break

    board.pop()
    return is_takeable


def leaves_undefended_piece(move, board):
    capture = board.is_capture(move)
    captured_something = False
    to_piece = board.piece_at(move.to_square)
    from_piece = board.piece_at(move.from_square)
    if to_piece:
        if capture and from_piece.piece_type <= to_piece.piece_type:
            captured_something = True
    board.push(move)
    is_undefended = False

    # After the move, for each of our pieces
    for square, piece in board.piece_map().items():
        if piece.color == board.turn or piece.piece_type == chess.PAWN:
            continue  # Skip enemy pieces

        attackers = board.attackers(board.turn, square)
        defenders = board.attackers(not board.turn, square)
        attacked_by_lower = True if [k for k in attackers if board.piece_at(k).piece_type < from_piece.piece_type] else False

        if len(attackers) > len(defenders) and not captured_something or attacked_by_lower:
            is_undefended = True
            break

    board.pop()
    return is_undefended


def leaves_undefended_pawn(move, board):
    capture = board.is_capture(move)
    # to_piece = board.piece_at(move.to_square)
    board.push(move)
    is_undefended = False

    # After the move, for each of our pieces
    for square, piece in board.piece_map().items():
        if piece.color == board.turn or piece.piece_type != chess.PAWN:
            continue  # Skip enemy pieces

        attackers = board.attackers(board.turn, square)
        defenders = board.attackers(not board.turn, square)

        if len(attackers) > len(defenders) and not capture:
            is_undefended = True
            break

    board.pop()
    return is_undefended


def leaves_undefended_queen(move, board):
    capture = board.is_capture(move)
    captured_queen = False
    to_piece = board.piece_at(move.to_square)
    if to_piece:
        if to_piece.piece_type == chess.QUEEN and capture:
            captured_queen = True
    board.push(move)
    is_undefended = False

    # After the move, for each of our pieces
    for square, piece in board.piece_map().items():
        if piece.color == board.turn or piece.piece_type != chess.QUEEN:
            continue  # Skip enemy pieces

        attackers = board.attackers(board.turn, square)
        defenders = board.attackers(not board.turn, square)
        attacked_by_queen = True if [k for k in attackers if board.piece_at(k).piece_type == chess.QUEEN] else False

        if attackers and not captured_queen and not all([attacked_by_queen, defenders, len(attackers == 1)]):
            is_undefended = True
            break

    board.pop()
    return is_undefended


def exposes_pieces_to_pawn(move, board):
    board.push(move)
    is_exposed = False

    # Check all our own pieces
    for square in board.piece_map():
        piece = board.piece_at(square)
        # if piece and piece.color != board.turn:  # board.turn is AFTER the move
        if piece and piece.color != board.turn and piece.piece_type != 1:  # board.turn is AFTER the move
            attackers = board.attackers(board.turn, square)
            for attacker_square in attackers:
                attacker = board.piece_at(attacker_square)
                if attacker and attacker.piece_type == chess.PAWN:
                    is_exposed = True
                    break
        if is_exposed:
            break

    board.pop()
    return is_exposed


def exposes_pawns_to_pawn(move, board):
    board.push(move)
    is_exposed = False

    # Check all our own pieces
    for square in board.piece_map():
        piece = board.piece_at(square)
        # if piece and piece.color != board.turn:  # board.turn is AFTER the move
        if piece and piece.color != board.turn and piece.piece_type == 1:  # board.turn is AFTER the move
            attackers = board.attackers(board.turn, square)
            for attacker_square in attackers:
                attacker = board.piece_at(attacker_square)
                if attacker and attacker.piece_type == chess.PAWN:
                    is_exposed = True
                    break
        if is_exposed:
            break

    board.pop()
    return is_exposed


def leaves_pawns_exposed_to_pawn(move, board):
    board.push(move)
    is_exposed = False

    # Check all our own pieces
    for square in board.piece_map():
        piece = board.piece_at(square)
        # if piece and piece.color == board.turn:  # board.turn is AFTER the move
        if piece and piece.color == board.turn and piece.piece_type == 1:  # board.turn is AFTER the move
            attackers = board.attackers(not board.turn, square)
            for attacker_square in attackers:
                attacker = board.piece_at(attacker_square)
                if attacker and attacker.piece_type == chess.PAWN:
                    is_exposed = True
                    break
        if is_exposed:
            break

    board.pop()
    return is_exposed


def leaves_piece_exposed_to_pawn(move, board):
    board.push(move)
    is_exposed = False

    # Check all our own pieces
    for square in board.piece_map():
        piece = board.piece_at(square)
        # if piece and piece.color == board.turn:  # board.turn is AFTER the move
        if piece and piece.color == board.turn and piece.piece_type != 1:  # board.turn is AFTER the move
            attackers = board.attackers(not board.turn, square)
            for attacker_square in attackers:
                attacker = board.piece_at(attacker_square)
                if attacker and attacker.piece_type == chess.PAWN:
                    is_exposed = True
                    break
        if is_exposed:
            break

    board.pop()
    return is_exposed


def is_safe_from_pawn(move, board):
    """Checks if the destination square is attacked by an enemy pawn."""
    board.push(move)
    is_attacked = any(
        board.piece_at(move.to_square) and piece.piece_type == chess.PAWN
        for square in board.attackers(not board.turn, move.to_square)
        if (piece := board.piece_at(square))
    )
    board.pop()
    return not is_attacked


def our_random_move(board):
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)  # For variety within safety

    # Prioritise capturing their queen
    for move in legal_moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece and captured_piece.piece_type == chess.QUEEN:
                print("Taking TC's queen 😎")
                return move

    # Filter out moves that hang our queen
    safe_moves = []
    shit_moves = []
    for move in legal_moves:
        from_rank = chess.square_rank(move.from_square)
        to_rank = chess.square_rank(move.to_square)
        rank_diff = to_rank - from_rank
        skip_move = False
        piece = board.piece_at(move.from_square)
        if not piece:
            continue

        # Simulate the move
        board.push(move)
        # attackers = board.attackers(not board.turn, move.to_square)
        if board.is_checkmate():
            safe_moves = [move]
            board.pop()
            continue
        check = 1 if board.is_check() else 0
        board.pop()
        shit_exclusions = set()

        # if piece.piece_type == chess.QUEEN and attackers:
        #     continue  # Don't hang the queen
        if exposes_pieces_to_pawn(move, board):
            # shit_moves.append((move, 3))
            shit_exclusions.add(3)
            skip_move = True  # Don't step into pawn danger
        # if exposes_pawns_to_pawn(move, board):
        #     # shit_moves.append((move, 3))
        #     shit_exclusions.add(-1)
        #     skip_move = True  # Don't step into pawn danger
        # if leaves_piece_exposed_to_pawn(move, board):
        #     # shit_moves.append((move, 0))
        #     shit_exclusions.add(0)
        #     skip_move = True  # Don't step into pawn danger
        # if leaves_pawns_exposed_to_pawn(move, board):
        #     # shit_moves.append((move, 0))
        #     shit_exclusions.add(-3)
        #     skip_move = True  # Don't step into pawn danger
        # Skip if it leaves any pieces undefended
        if leaves_undefended_piece(move, board):
            # shit_moves.append((move, 2))
            shit_exclusions.add(2)
            skip_move = True
        if leaves_undefended_pawn(move, board):
            # shit_moves.append((move, 2))
            shit_exclusions.add(-1)
            skip_move = True
        # if leaves_takeable_piece(move, board):
        #     # shit_moves.append((move, 1))
        #     shit_exclusions.add(-2)
        #     skip_move = True
        if leaves_undefended_queen(move, board):
            # shit_moves.append((move, 4))
            shit_exclusions.add(4)
            skip_move = True
        if allows_mate_in_one(move, board):
            # shit_moves.append((move, 5))
            shit_exclusions.add(5)
            skip_move = True

        # capture_bonus = -2 if board.is_capture(move) else 0
        capture = 1 if board.is_capture(move) else 0
        en_passant = 1 if board.is_en_passant(move) else 0
        if en_passant or not capture:
            capture_piece = 0
        else:
            capture_piece = 1 if board.piece_at(move.to_square).piece_type != 1 else 0
        # check = 1 if board.is_check(move) else 0
        castling = 1 if board.is_castling(move) else 0
        zeroing = 1 if board.is_zeroing(move) else 0

        move_rating = (en_passant, capture_piece, capture, check, castling, rank_diff * sign, zeroing)

        if shit_exclusions:
            shit_moves.append((move, -max(shit_exclusions), move_rating))

        if skip_move:
            continue

        safe_moves.append((move, move_rating))

    # Prefer safe moves, fall back to random legal
    if safe_moves:
        return sorted(safe_moves, key=lambda k: k[1], reverse=True)[0][0]
        # return random.choice(safe_moves)
    elif shit_moves:
        print("No good moves! Playing random shite move...")
        return sorted(shit_moves, key=lambda k: (k[1], k[2]), reverse=True)[0][0]
    else:
        print("No safe moves! Playing random legal move...")
        return random.choice(legal_moves)


def tcs_thickest_move_youve_ever_seen(board):
    while True:
        move_input = input("TC's move (or type 'undo' or 'stop'): ").strip().lower()
        if move_input == "stop":
            return "stop"
        elif move_input == "undo":
            return "undo"
        try:
            move = board.parse_san(move_input)
            return move
        except ValueError:
            print("Invalid move, try again.")


# Game setup
board = chess.Board()

# Choose side
black_or_white = input("w for white and b for black: ").strip().lower()
if black_or_white == "w":
    sign = 1
    my_move = our_random_move(board)
    board.push(my_move)
    print(board)
else:
    sign = -1

# Main game loop
while True:
    dumb_move = tcs_thickest_move_youve_ever_seen(board)

    if dumb_move == "stop":
        print("Game stopped.")
        break
    elif dumb_move == "undo":
        if len(board.move_stack) >= 2:
            board.pop()  # Undo our move
            board.pop()  # Undo TC's move
            print("Undid last turn.")
            print(board)
        else:
            print("Not enough moves to undo.")
        continue

    board.push(dumb_move)
    print(board)

    if board.is_checkmate():
        print("TC checkmates you. Game over.")
        break

    my_move = our_random_move(board)
    board.push(my_move)
    print("Your move:")
    print(my_move)

    if board.is_checkmate():
        print("You checkmate TC. Game over. Nice one.")
        break
