import os
import time
import random
import curses

# Global variables
food = []
enemy = []
black_hole = []
player = []
score = 0
enemy_move_interval = 0.1
last_enemy_move_time = time.time()
num_food_items = random.randint(1, 20)
num_enemy = random.randint(5, 8)
num_black_hole = random.randint(1, 2)
play = True
current_time = time.time()
maxl = 0
maxc = 0
food_age = 100
player_char = '🛸'
enemy_char = '👾'
food_char = '🍕'
black_hole_char = '🌀'

def init_curses(stdscr):
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    print("Curses initialized.")

def random_place(world, maxl, maxc):
    while True:
        a = random.randint(0, maxl - 1)
        b = random.randint(0, maxc - 1)
        if world[a][b] == ' ':
            return a, b

def init_world(stdscr):
    global world, player, food, enemy, black_hole
    world = []
    for i in range(maxl + 1):
        world.append([])
        for j in range(maxc + 1):
            if random.random() > 0.05:
                world[i].append(' ')
            else:
                world[i].append('.')
    
    for _ in range(num_food_items):
        fl, fc = random_place(world, maxl, maxc)
        fa = random.randint(food_age, food_age * 10)
        food.append((fl, fc, fa, food_char))   

    for _ in range(num_enemy):
        el, ec = random_place(world, maxl, maxc)
        enemy.append((el, ec, enemy_char))  

    for _ in range(num_black_hole):
        bl, bc = random_place(world, maxl, maxc)
        black_hole.append((bl, bc, black_hole_char))
    
    player_l, player_c = random_place(world, maxl, maxc)
    player = [player_l, player_c, player_char]
    print("World initialized.")

def in_range(a, min_val, max_val):
    return max(min(a, max_val), min_val)

def draw(stdscr):
    stdscr.clear()
    for i in range(maxl):
        for j in range(maxc):
            stdscr.addch(i, j, world[i][j])
    # Show the score of the player
    stdscr.addstr(1, 1, f"Score: {score}")

    # Draw food
    for f in food:
        fl, fc, fa, fch = f
        stdscr.addch(fl, fc, fch)

    # Draw enemies
    for e in enemy:
        el, ec, ech = e
        stdscr.addch(el, ec, ech)

    # Draw black holes  
    if score > 50:
        for b in black_hole:
            bl, bc, bch = b
            stdscr.addch(bl, bc, bch)

    # Draw player  
    pl, pc, pch = player
    stdscr.addch(pl, pc, pch)
    stdscr.refresh()

def move_player(key):
    if key in ['w', 'W'] and world[player[0] - 1][player[1]] != '.':
        player[0] -= 1
    elif key in ['s', 'S'] and world[player[0] + 1][player[1]] != '.':
        player[0] += 1
    elif key in ['d', 'D'] and world[player[0]][player[1] + 1] != '.':
        player[1] += 1
    elif key in ['a', 'A'] and world[player[0]][player[1] - 1] != '.':
        player[1] -= 1

    player[0] = in_range(player[0], 0, maxl - 1)
    player[1] = in_range(player[1], 0, maxc - 1)

def check_food():
    global score
    for i in range(len(food)):
        fl, fc, fa, fch = food[i]
        fa -= 1
        if player[0] == fl and player[1] == fc:
            score += 10
            fl, fc = random_place(world, maxl, maxc)
            fa = random.randint(food_age, food_age * 10)
            food[i] = (fl, fc, fa, fch)
        if fa <= 0:
            fl, fc = random_place(world, maxl, maxc)
            fa = random.randint(food_age, food_age * 10)
        food[i] = (fl, fc, fa, fch)

def check_black_hole(stdscr):
    if score > 50:
        for i in range(len(black_hole)):
            bl, bc, bch = black_hole[i]
            if player[0] == bl and player[1] == bc:
                curses.endwin()
                stdscr.clear()
                stdscr.addstr(maxl // 2, maxc // 2, "!!! YOU FOUND A HIDDEN WAY TO INTERSTELLAR JOURNEY !!!")
                stdscr.refresh()
                time.sleep(5)
                exit()

def move_enemy(stdscr):
    global play
    for e in range(len(enemy)):
        el, ec, ech = enemy[e]
       
        if random.random() > 0.8 and el > player[0]:
            el -= 1
        elif random.random() > 0.8 and  el < player[0]:
            el += 1
        if random.random() > 0.8 and ec < player[1]:
            ec += 1
        elif random.random() > 0.8 and  ec > player[1]:
            ec -= 1

        el = in_range(el, 0, maxl - 1)
        ec = in_range(ec, 0, maxc - 1)

        enemy[e] = (el, ec, ech)

        if el == player[0] and ec == player[1]:
            stdscr.addstr(maxl // 2, maxc // 2, "YOU DIED!!!!")
            stdscr.refresh()
            time.sleep(3)
            play = False

def run(stdscr):
    global play, current_time
    while play:
        current_time = time.time()
        try:
            key = stdscr.getkey()    
        except:
            key = ' '
        if key == 'q':
            play = False
        elif key == 'r':
            init_world(stdscr)
            draw(stdscr)               
        elif key in 'awsdASWD':
            move_player(key)   

        move_enemy(stdscr)
        check_food()
        check_black_hole(stdscr)
        
        draw(stdscr)
        time.sleep(0.01)

def main(stdscr):
    global maxl, maxc
    maxl = curses.LINES - 1
    maxc = curses.COLS - 1

    print("Initializing curses...")
    init_curses(stdscr)
    print("Initializing world...")
    init_world(stdscr)
    print("Starting game loop...")
    run(stdscr)

if __name__ == "__main__":
    try:
        print("Starting game...")
        curses.wrapper(main)
    except KeyboardInterrupt:
        curses.endwin()
        print("Exited program")
    except Exception as e:
        curses.endwin()
        print(f"An error occurred: {e}")
