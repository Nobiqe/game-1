import os
import time
import random
import curses

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.maxl = curses.LINES - 1
        self.maxc = curses.COLS - 1
        self.food_age = 100
        self.player_char = '🛸'
        self.enemy_char = '👾'
        self.food_char = '🍕'
        self.black_hole_char = '🌀'
        
        self.food = []
        self.enemy = []
        self.black_hole = []
        self.player = []

        self.score = 0
        self.enemy_move_interval = 0.1
        self.last_enemy_move_time = time.time()
        self.num_food_items = random.randint(1, 20)
        self.num_enemy = random.randint(5 ,8)
        self.num_black_hole = random.randint(1, 2)
        self.play = True
        self.current_time = time.time()
        
        print("Initializing curses...")
        self.init_curses()
        print("Initializing world...")
        self.init_world()
        print("Starting game loop...")
        self.run()

    def init_curses(self):
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        print("Curses initialized.")

    def random_place(self):
        while True:
            a = random.randint(0, self.maxl - 1)
            b = random.randint(0, self.maxc - 1)
            if self.world[a][b] == ' ':
                return a, b

    def init_world(self):
        self.world = []
        for i in range(self.maxl + 1):
            self.world.append([])
            for j in range(self.maxc + 1):
                if random.random() > 0.05:
                    self.world[i].append(' ')
                else:
                    self.world[i].append('.')
        
        for _ in range(self.num_food_items):
            fl, fc = self.random_place()
            fa = random.randint(self.food_age, self.food_age * 10)
            self.food.append((fl, fc, fa, self.food_char))   

        for _ in range(self.num_enemy):
            el, ec = self.random_place()
            self.enemy.append((el, ec, self.enemy_char))  

        for _ in range(self.num_black_hole):
            bl, bc = self.random_place()
            self.black_hole.append((bl, bc, self.black_hole_char))
        
        player_l, player_c = self.random_place()
        self.player = [player_l, player_c, self.player_char]
        print("World initialized.")

    def in_range(self, a, min_val, max_val):
        return max(min(a, max_val), min_val)
    
    def draw(self):
        self.stdscr.clear()
        for i in range(self.maxl):
            for j in range(self.maxc):
                self.stdscr.addch(i, j, self.world[i][j])
        # Show the score of the player
        self.stdscr.addstr(1, 1, f"Score: {self.score}")

        # Draw food
        for f in self.food:
            fl, fc, fa, fch = f
            self.stdscr.addch(fl, fc, fch)

        # Draw enemies
        for e in self.enemy:
            el, ec, ech = e
            self.stdscr.addch(el, ec, ech)

        
        # Draw black holes  
        if self.score > 50:
            for b in self.black_hole:
                bl, bc, bch = b
                self.stdscr.addch(bl, bc, bch)

        # Draw player  
        pl, pc, pch = self.player
        self.stdscr.addch(pl, pc, pch)
        self.stdscr.refresh()

    def move_player(self, key):
        if key in ['w', 'W'] and self.world[self.player[0] - 1][self.player[1]] != '.':
            self.player[0] -= 1
        elif key in ['s', 'S'] and self.world[self.player[0] + 1][self.player[1]] != '.':
            self.player[0] += 1
        elif key in ['d', 'D'] and self.world[self.player[0]][self.player[1] + 1] != '.':
            self.player[1] += 1
        elif key in ['a', 'A'] and self.world[self.player[0]][self.player[1] - 1] != '.':
            self.player[1] -= 1

        self.player[0] = self.in_range(self.player[0], 0, self.maxl - 1)
        self.player[1] = self.in_range(self.player[1], 0, self.maxc - 1)

    def check_food(self):
        for i in range(len(self.food)):
            fl, fc, fa, fch = self.food[i]
            fa -= 1
            if self.player[0] == fl and self.player[1] == fc:
                self.score += 10
                fl, fc = self.random_place()
                fa = random.randint(self.food_age, self.food_age * 10)
                self.food[i] = (fl, fc, fa, fch)
            if fa <= 0:
                fl, fc = self.random_place()
                fa = random.randint(self.food_age, self.food_age * 10)
            self.food[i] = (fl, fc, fa, fch)


    def check_black_hole(self):
        if self.score > 50:
            for i in range(len(self.black_hole)):
                bl, bc, bch = self.black_hole[i]
                if self.player[0] == bl and self.player[1] == bc:
                    curses.endwin()
                    self.stdscr.clear()
                    self.stdscr.addstr(self.maxl // 2, self.maxc // 2, "!!! YOU FOUND A HIDDEN WAY TO INTERSTELLAR JOURNEY !!!")
                    self.stdscr.refresh()
                    time.sleep(5)
                    exit()

    def  move_enemy(self):
        for e in range(len(self.enemy)):
            el , ec ,ech = self.enemy[e]
           
            if random.random() > 0.8 and el > self.player[0]:
                el -= 1
            elif random.random() > 0.8 and  el < self.player[0]:
                el += 1
            if random.random() > 0.8 and ec < self.player[1]:
                ec += 1
            elif random.random() > 0.8 and  ec > self.player[1]:
                ec -= 1

            el = self.in_range(el, 0, self.maxl - 1)
            ec = self.in_range(ec, 0, self.maxc - 1)

            self.enemy[e] = (el ,ec ,ech)

            if el == self.player[0] and ec == self.player[1]:
                self.stdscr.addstr(self.maxl // 2, self.maxc // 2, "YOU DIED!!!!")
                self.stdscr.refresh()
                time.sleep(3)
                self.play = False                  
    def run(self):
        while self.play:
            self.current_time = time.time()
            try:
                key = self.stdscr.getkey()    
            except:
                key = ' '
            if key == 'q':
                self.play = False
            elif key == 'r':
                self.init_world()
                self.draw()               
            elif key in 'awsdASWD':
                self.move_player(key)   

            self.move_enemy()
            self.check_food()
            self.check_black_hole()
            

            self.draw()
            time.sleep(0.01)


if __name__ == "__main__":
    try:
        print("Starting game...")
        curses.wrapper(Game)
    except KeyboardInterrupt:
        curses.endwin()
        print("Exited program")
    except Exception as e:
        curses.endwin()
        print(f"An error occurred: {e}")
