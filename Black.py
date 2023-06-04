import chess
import chess.engine
import chess.pgn
import os
import pygame

# Inicijalizacija Pygame-a
pygame.init()

# Definisanje dimenzija ekrana i boja
BORDER_WIDTH = 50
SCREEN_WIDTH = 800 + 2 * BORDER_WIDTH
SCREEN_HEIGHT = 800 + 2 * BORDER_WIDTH
FPS = 10
WHITE = (218, 233, 242)
BLACK = (110, 153, 192)
DARK_GREEN = (0, 100, 0)

def get_piece_name(piece):
    if piece.color == chess.WHITE:
        color = "w"
    else:
        color = "b"

    return color + piece.symbol().lower()

def display_move(move: chess.Move, board: chess.Board) -> None:
    turn_name = "Black" if board.turn == chess.BLACK else "White"
    move_san = board.san(move)  
    print("{} played: {}".format(turn_name, move_san))

def load_images():
    images = {}
    pieces = ['bp', 'br', 'bn', 'bb', 'bq', 'bk',
              'wp', 'wr', 'wn', 'wb', 'wq', 'wk']
    for piece in pieces:
        images[piece] = pygame.image.load(f"Resources/{piece}.png")
    for piece_type in chess.PIECE_TYPES:
        if piece_type not in [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]:
            continue
        for color in [chess.WHITE, chess.BLACK]:
            piece_name = chess.piece_name(piece_type).lower()
            color_name = 'w' if color == chess.WHITE else 'b'
            key = color_name + piece_name
            if key not in images:
                images[key] = pygame.image.load(f"Resources/{key}.png")
    return images

def draw(screen, board, selected_square, pieces):
    square_size = 800 // 8
    for row in range(8):
        for col in range(8):
            rect = pygame.Rect(BORDER_WIDTH + col * square_size, BORDER_WIDTH + (7 - row) * square_size, square_size, square_size)
            pygame.draw.rect(screen, BLACK if (row + col) % 2 == 0 else WHITE, rect)

            piece = board.piece_at((7 - row) * 8 + (7 - col))
            if piece:
                piece_image = pieces[get_piece_name(piece)]
                screen.blit(piece_image, rect.topleft)

    if selected_square is not None:
        rect = pygame.Rect(BORDER_WIDTH + (7 - selected_square[0]) * square_size, BORDER_WIDTH + selected_square[1] * square_size, square_size, square_size)
        pygame.draw.rect(screen, (0, 255, 0), rect, 5)

    # Draw border and coordinates
    pygame.draw.rect(screen, DARK_GREEN, (0, 0, SCREEN_WIDTH, BORDER_WIDTH))  # Top border
    pygame.draw.rect(screen, DARK_GREEN, (0, SCREEN_HEIGHT - BORDER_WIDTH, SCREEN_WIDTH, BORDER_WIDTH))  # Bottom border
    pygame.draw.rect(screen, DARK_GREEN, (0, 0, BORDER_WIDTH, SCREEN_HEIGHT))  # Left border
    pygame.draw.rect(screen, DARK_GREEN, (SCREEN_WIDTH - BORDER_WIDTH, 0, BORDER_WIDTH, SCREEN_HEIGHT))  # Right border


    font = pygame.font.Font(None, 36)
    letters = 'hgfedcba'
    numbers = '12345678'
    for i in range(8):
        letter_text = font.render(letters[i], True, WHITE)
        number_text = font.render(numbers[i], True, WHITE)
        screen.blit(letter_text, (BORDER_WIDTH + i * square_size + square_size // 2 - letter_text.get_width() // 2, BORDER_WIDTH // 2 - letter_text.get_height() // 2))
        screen.blit(number_text, (BORDER_WIDTH // 2 - number_text.get_width() // 2, BORDER_WIDTH + i * square_size + square_size // 2 - number_text.get_height() // 2))
        screen.blit(letter_text, (BORDER_WIDTH + i * square_size + square_size // 2 - letter_text.get_width() // 2, SCREEN_HEIGHT - BORDER_WIDTH // 2 - letter_text.get_height() // 2))
        screen.blit(number_text, (SCREEN_WIDTH - BORDER_WIDTH // 2 - number_text.get_width() // 2, BORDER_WIDTH + i * square_size + square_size // 2 - number_text.get_height() // 2))

#```python
def get_square(pos):
    board_size = SCREEN_HEIGHT - 2 * BORDER_WIDTH
    square_size = board_size // 8

    # Provera da li su koordinate miša unutar granica šahovske table
    if pos[0] < BORDER_WIDTH or pos[0] >= SCREEN_WIDTH - BORDER_WIDTH or pos[1] < BORDER_WIDTH or pos[1] >= SCREEN_HEIGHT - BORDER_WIDTH:
        return None

    adjusted_pos = (pos[0] - BORDER_WIDTH, pos[1] - BORDER_WIDTH)
    row = 7 - (adjusted_pos[0] // square_size)
    col = 7 - (adjusted_pos[1] // square_size)

    return (row, 7 - col)
#```

# Glna funkcija
def choose_color():
    print("Odaberite boju figura kojima želite igrati:")
    print("1. Bele figure")
    print("2. Crne figure")
    choice = 0
    while choice not in (1, 2):
        try:
            choice = int(input("Unesite broj (1 ili 2): "))
        except ValueError:
            pass
    return chess.WHITE if choice == 1 else chess.BLACK

def set_game_result(board):
    if board.is_stalemate():
        result = "1/2-1/2"
    elif board.is_insufficient_material():
        result = "1/2-1/2"
    elif board.can_claim_threefold_repetition():
        result = "1/2-1/2"
    elif board.is_checkmate():
        if board.turn:
            result = "0-1"
        else:
            result = "1-0"
    else:
        result = "*"

    return result

def save_game_to_pgn(board, engine, game_result):
    result = set_game_result(board)
    new_game = chess.pgn.Game.from_board(board)
    new_game.headers["Result"] = result

    new_game.headers["White"] = "{}".format(engine.id["name"])
    new_game.headers["Black"] = "Human"

    pgn_file = "game.pgn"
    if os.path.exists(pgn_file):
        with open(pgn_file, "r") as pgn:
            games = [chess.pgn.read_game(pgn) for _ in pgn]
    else:
        games = []

    games.append(new_game)

    with open(pgn_file, "w") as pgn_file:
        for game in games:
            pgn_file.write(str(game) + "\n\n")

def check_draw_conditions(board: chess.Board) -> str:
    if board.can_claim_draw():
        return "1/2-1/2"
    if board.can_claim_threefold_repetition():
        return "1/2-1/2"
    if board.halfmove_clock >= 100:
        return "1/2-1/2"
    return None

def main():
    player_color = choose_color()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Šah")

    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\Public\\Documents\\White_and_Black-main\\komodo-14.1-64bit.exe")

    pieces = load_images()  # Load images for each chess piece

    selected_square = None
    running = True

    clock = pygame.time.Clock()  

    # Initialize game_result variable
    game_result = None

    while running:
        clock.tick(FPS)  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == player_color:
                pos = pygame.mouse.get_pos()
                selected_square = get_square(pos)
            elif event.type == pygame.MOUSEBUTTONUP and board.turn == player_color:
                pos = pygame.mouse.get_pos()
                target_square = get_square(pos)
                if selected_square is not None and target_square is not None:
                    move = chess.Move(selected_square[1] * 8 + selected_square[0], target_square[1] * 8 + target_square[0])
                    if move in board.legal_moves:
                        display_move(move, board)  # Display the move before pushing it
                        board.push(move)
                        
                selected_square = None

        draw(screen, board, selected_square, pieces)  # Pass the 'pieces' dictionary to the 'draw_board' function

        # Postavljanje table na donji levi ugao ekrana
        board_rect = screen.get_rect()
        board_rect.bottomleft = (0, SCREEN_HEIGHT)
        screen.blit(screen, board_rect)

        pygame.display.flip()

        draw_result = check_draw_conditions(board)
        if draw_result:
            running = False
            game_result = draw_result
            continue

        if board.turn != player_color:
            result = engine.play(board, chess.engine.Limit(time=2.0))
            display_move(result.move, board)
            board.push(result.move)

            draw_result = check_draw_conditions(board)
            if draw_result:
                running = False
                game_result = draw_result
                continue

        if check_draw_conditions(board):  # Added check_draw_conditions call here
            break  
        
        if board.turn != player_color:
            result = engine.play(board, chess.engine.Limit(time=2.0))
            display_move(result.move, board)  
            board.push(result.move)

            if check_draw_conditions(board):  # Added check_draw_conditions call here
                break  

    # Set game_result if it's not already set
    if game_result is None:
        game_result = set_game_result(board)

    save_game_to_pgn(board, engine, game_result)

    engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
