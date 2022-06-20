import random
import pygame
from queue import Queue
pygame.init()

WIDTH, HEIGHT = 700,700

win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Minesweeper")

BG_COLOR = (255,255,255)
ROWS, COLS = 20,20
MINES = 75
SIZE = WIDTH / ROWS

NUM_FONT = pygame.font.SysFont("verdana", 25, True)
NUM_COLORS = {1: (21,37,204), 2: (166,243,246), 3: (96,238,131), 4: (226,228,204), 5: (225,211,171), 6: "purple", 7: "orange", 8: "pink"}
RECT_COLOR = (164, 164, 164)
CLICKED_RECT_COLOR = (140,140,140)  
BORDER_COLOR = (82, 82, 82)
FLAG = pygame.image.load(r'images\red-flag.png')
FLAG = pygame.transform.scale(FLAG, (SIZE, SIZE))
MINE = pygame.image.load(r'images\bomb.png')
MINE = pygame.transform.scale(MINE, (SIZE, SIZE))
HAPPY_FACE = pygame.image.load(r'images\happiness.png')
HAPPY_FACE = pygame.transform.scale(HAPPY_FACE, (SIZE, SIZE))
LOST_FONT = pygame.font.SysFont("lucidaconsole", 50)
WIN_FONT = pygame.font.SysFont("lucidaconsole", 50)

# returns neighbors around square at row, col
def get_neighbors(row, col, rows, cols): 
    neighbors = []
    
    if row > 0: # UP 
        neighbors.append((row - 1, col))
    if row < rows - 1: # DOWN
        neighbors.append((row + 1, col))
    if col > 0: # LEFT
        neighbors.append((row, col - 1))
    if col < cols - 1: # RIGHT
        neighbors.append((row, col + 1))
    
    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))
    
    return neighbors

# randomly generate mines in field[][]
def create_mine_field(rows, cols, mines): 
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()
    
    while len(mine_positions) < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue

        mine_positions.add(pos)
        field[row][col] = -1

    # get neighbors of mines, assign numbers to surrounding squares
    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1
    
    return field

# draw boxes 
# is_winner = smiley faces where all of the mines are
# is_loser = mines revealed
def draw(win, field, cover_field, is_winner=False, is_loser=False):
    win.fill(BG_COLOR)

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            # covered: cover_field[i][j] == 0
            # uncovered: cover_field[i][j] == 1
            # flagged: cover_field[i][j] == -2
            # mine: field[i][j] == -1
            # regular numbers: field[i][j] is 1 to 8
            is_covered = cover_field[i][j] == 0 
            is_flag = cover_field[i][j] == -2
            is_mine = value == -1

            if is_winner:
                if is_flag:
                    win.blit(HAPPY_FACE,(x,y))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                if is_covered:
                    pygame.draw.rect(win, RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    continue
                else:
                    pygame.draw.rect(win, CLICKED_RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    if is_mine:
                        win.blit(HAPPY_FACE,(x,y))
                        pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
            elif is_loser:
                if is_covered:
                    pygame.draw.rect(win, RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    continue
                else:
                    pygame.draw.rect(win, CLICKED_RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                if is_mine:
                    win.blit(MINE,(x,y))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
            else:
                if is_flag:
                    win.blit(FLAG,(x,y))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    continue

                if is_covered:
                    pygame.draw.rect(win, RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    continue
                else:
                    pygame.draw.rect(win, CLICKED_RECT_COLOR, (x,y, SIZE, SIZE))
                    pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
                    if is_mine:
                        win.blit(MINE,(x,y))
                        pygame.draw.rect(win, BORDER_COLOR, (x,y, SIZE, SIZE), 2)
            
            if value > 0:
                text = NUM_FONT.render(str(value), 1, NUM_COLORS[value])
                win.blit(text, (x + (SIZE/2 - text.get_width()/2), y + (SIZE/2 - text.get_height()/2)))

    pygame.display.update()

# returns row, col where mouse is
def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)

    return row, col

# if empty tile is clicked on, search for other empty tiles and reveal them
def uncover_from_pos(row, col, cover_field, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty(): # if empty tile or #, uncover
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r,c in neighbors:
            if (r,c) in visited:
                continue
                
            value = field[r][c]
            if value == 0 and cover_field[r][c] != -2:
                q.put((r,c))

            if cover_field[r][c] != -2:
                cover_field[r][c] = 1
            visited.add((r,c))

# if n number is clicked on with n surrounding flags, reveal neighbors
# if flag is misplaced (one of neighbors is mine), end game
def reveal_neighbors(row, col, cover_field, field):
    neighbors = get_neighbors(row, col, ROWS, COLS)
    flags = 0
    for r,c in neighbors:
        if cover_field[r][c] == -2:
            flags += 1 
    if flags == field[row][col]:
        for r,c in neighbors:
            if cover_field[r][c] != -2 and field[r][c] != -1:
                cover_field[r][c] = 1
            if field[r][c] == 0:
                uncover_from_pos(r, c, cover_field, field)
            if cover_field[r][c] != -2 and field[r][c] == -1:
                cover_field[r][c] = 1
                return r,c
    return 0,0

# loss text
def draw_lost(win,text):
    text = LOST_FONT.render(text, 1, "black")
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    pygame.display.update()
    
# win text
def draw_win(win,text):
    text = WIN_FONT.render(text, 1, "black")
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    pygame.display.update()

def main():
    run = True
    field = create_mine_field(ROWS, COLS, MINES)
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    clicks = 0
    winner = False
    loser = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue

                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and cover_field[row][col] != -2: 
                    cover_field[row][col] = 1 # uncovered
                    reveal_neighbors(row, col, cover_field, field) 
                    r,c = reveal_neighbors(row, col, cover_field, field)
                    if r != 0 and c!= 0: 
                        loser = True
                    else: # when reveal_neighbors returns 0,0 then flag was misplaced
                        loser = False
 
                    if field[row][col] == -1: # clicked on mine
                        loser = True
                    
                    if field[row][col] == 0:
                        uncover_from_pos(row, col, cover_field, field)
                    clicks += 1

                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                    elif cover_field[row][col] == 1:
                        continue
                    else:
                        cover_field[row][col] = -2
                
        for i in range(0, ROWS): # checks for win condition
            if any(x == 0 for x in cover_field[i]):
                break
            if i == ROWS-1:
                winner = True

        if loser: # resets after loss
            draw(win, field, cover_field, winner, loser)
            draw_lost(win, "You lose! D:")
            pygame.time.delay(5000)
            
            field = create_mine_field(ROWS, COLS, MINES)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            loser = False


        if winner: # resets after win
            draw(win, field, cover_field, winner, loser)
            draw_win(win, "You WIN! :)")
            pygame.time.delay(7000)

            field = create_mine_field(ROWS, COLS, MINES)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = MINES
            clicks = 0
            winner = False

        draw(win, field, cover_field, False)
    
    pygame.quit()

if __name__ == "__main__":
    main()



