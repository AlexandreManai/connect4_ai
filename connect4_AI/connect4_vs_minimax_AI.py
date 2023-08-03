'''
ways to make it better:
 - even-odd strategy 
 - evaluate_window() -> optimize evaluation videos
'''

import numpy as np
import random
import pygame
import sys
import math

BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = 2

EMPTY = 0
WINDOW_SIZE = 4

# could have went for math library
PLUS_INF = 10000000000000000000
MINUS_INF = -10000000000000000000

def create_board():
  board = np.zeros((ROW_COUNT,COLUMN_COUNT))
  return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def  get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

# test for winning move 
def winning_move(board, piece):
    # check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # check vertical locations for win
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # check positively sloped diagnols
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # check negatively sloped diagnols
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# look into how to optimize scoring points
def evaluate_window(window, piece):
    score = 0

    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score += 4

    return score

def score_position(board, piece):
    # score horizontal
    score = 0
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_SIZE]
            score += evaluate_window(window, piece)

    # score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_SIZE]
            score += evaluate_window(window, piece)

    # score positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_SIZE)]
            score += evaluate_window(window, piece)

    # score negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_SIZE)]
            score += evaluate_window(window, piece)

    # score center & '//' floor division
    cen_array = [int(i) for i in list(board[:,COLUMN_COUNT//2])]
    cen_count = cen_array.count(piece)
    score += cen_count * 6

    return score

def full_board(board):
    return len(get_valid_locations(board)) == 0

def terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or full_board(board)

def minimax(board, depth, alpha, beta, max_player):
    valid_locations = get_valid_locations(board)
    is_terminal = terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (PLUS_INF, None)
            elif winning_move(board, PLAYER_PIECE):
                return (MINUS_INF, None)
            else:
                return (0, None)
        else:
            return (score_position(board, AI_PIECE), None)
    if max_player:
        value = MINUS_INF # arbitrary value
        col = random.choice(valid_locations)
        for column in valid_locations:
            row = get_next_open_row(board, column)
            b_copy = board.copy()
            drop_piece(b_copy, row, column, AI_PIECE)
            new_value = minimax(b_copy, depth-1, alpha, beta ,False)[0]
            if value < new_value:
                value = new_value
                col = column
            alpha = max(alpha, new_value) 
            if beta <= alpha:
                break   
        return value, col 

    else:
        value = PLUS_INF # arbitrary value
        col = random.choice(valid_locations)
        for column in valid_locations:
            row = get_next_open_row(board, column)
            b_copy = board.copy()
            drop_piece(b_copy, row, column, PLAYER_PIECE)
            new_value = minimax(b_copy, depth-1, alpha, beta, True)[0]
            if value > new_value:
                value = new_value
                col = column
            beta = min(beta, new_value)
            if beta <= alpha:
               break    
        return value, col     

# needed to not make invalid moves while choosing best one
def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# draw board fully everytime
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            rect = pygame.Rect(c*(SQUARESIZE), r*(SQUARESIZE), SQUARESIZE-1, SQUARESIZE-1)
            pygame.draw.rect(screen, WHITE, rect)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                rect = pygame.Rect(c*(SQUARESIZE), height - (r*(SQUARESIZE)+ SQUARESIZE), SQUARESIZE-1, SQUARESIZE-1)
                pygame.draw.rect(screen, RED, rect)
            elif board[r][c] == AI_PIECE:
                rect = pygame.Rect(c*(SQUARESIZE), height - (r*(SQUARESIZE)+SQUARESIZE), SQUARESIZE-1, SQUARESIZE-1)
                pygame.draw.rect(screen, YELLOW, rect)
    pygame.display.update()



board = create_board()
print_board(board)
game_over = False
turn = random.randint(PLAYER, AI)  # randomly who starts
move = 0  # avoid useless checks

# int() is needed because else it would be a string because of input()

pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = ROW_COUNT * SQUARESIZE

size = (width, height)

screen = pygame.display.set_mode(size)

draw_board(board)
pygame.display.update()

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            #print(event.pos)
            # Your input
            if turn == PLAYER:
                 posx = event.pos[0]
                 col = int(math.floor(posx/SQUARESIZE))

                 if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    move += 1

                    if winning_move(board, PLAYER_PIECE) and move >= 7:
                         game_over = True

                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

    # AI input
    if turn == AI and not game_over:

        col =  minimax(board, 5, MINUS_INF, PLUS_INF, True)[1] #pick_be st_move(board, AI_PIECE)

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            move += 1

            if winning_move(board, AI_PIECE) and move >= 7:
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)