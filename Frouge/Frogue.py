import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Window Setup
pygame.display.set_caption("Frogue")

cell_size = 5
cols, rows = 100, 100

tiles = { #Tile Identifiers
    0: (30, 30, 30),#Void
    1: (50, 50, 50),#Floor 1
    2: (70, 70, 70),#Floor 2
    3: (120, 120, 120),#Wall 1
    4: (150, 150, 150),#Wall 2
    5: (50, 200, 50),#Player
    6: (200, 50, 50),#Enemy
    7 : (50, 50, 200),#Loot
}
stats = { # weapon stats
            "name": "",
            "numeric": 0,
            "range": 0,
            "radius": 0,
            "effect": "",
            "price": 0,
            }

class Camera():
    def __init__(self, screen_width, screen_height, catching = 0.1):
        self.offset = pygame.Vector2(0, 0)
        self.screen_width = screen_width # Width of camera view
        self.screen_height = screen_height # Hieght of camera view
        self.catching = catching # Camera catch up speed

    def center_on(self, target_pos): # controls offset to center on desired position
        desired_offset_x = target_pos[0] - self.screen_width // 2
        desired_offset_y = target_pos[1] - self.screen_height // 2
        self.offset.x += (desired_offset_x - self.offset.x) * self.catching # Smoothly move toward the desired offset
        self.offset.y += (desired_offset_y - self.offset.y) * self.catching

    def grid_to_screen(self, rect): # converts grid position to pixel position on screen
        return rect.move(-self.offset.x, -self.offset.y)

class Player(): #Player Manager
    def __init__(self, grid_x, grid_y, cell_size, dungeon_grid):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_size = cell_size
        self.dungeon_grid = dungeon_grid
        self.previous_tile = random.randint(1, 2)

    def position (self, px, py):
        self.grid_x = px # Update player grid x position
        self.grid_y = py # Update player grid y position
        self.dungeon_grid[py][px] = 5 # Set player position on grid

    def camera_position(self): # gets x, y position for camera
        return (self.grid_x * self.cell_size + self.cell_size // 2, self.grid_y * self.cell_size + self.cell_size // 2)

    def attack(self, target):
        print(target)
        #target.die()

    def move(self, dx, dy):
        if self.dungeon_grid[self.grid_y + dy][self.grid_x + dx] in (1, 2): # floor check
            self.dungeon_grid[self.grid_y][self.grid_x] = self.previous_tile # reset previous tile
            self.grid_x += dx # new x
            self.grid_y += dy # new y
            self.previous_tile = self.dungeon_grid[self.grid_y][self.grid_x] # store new previous tile
            self.position(self.grid_x, self.grid_y) # move player
        elif self.dungeon_grid[self.grid_y + dy][self.grid_x + dx] == 6: # enemy check
            self.attack(self.dungeon_grid[self.grid_y + dy][self.grid_x + dx])
        elif self.dungeon_grid[self.grid_y + dy][self.grid_x + dx] == 7: # loot check
            print("Loot")

class Enemy(): #Enemy Manager
    def __init__(self, grid_x, grid_y, cell_size, dungeon_grid,item):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_size = cell_size
        self.dungeon_grid = dungeon_grid
        self.item = item
        self.previous_tile = random.randint(1, 2)
        self.enemy = [] # Enemy List
        self.stats = { # Enemy Stats
            "health": 0,
            "numeric": 0,
            "range": 0,
            "radius": 0,
            "effect": "",
            "vision": 0,
            }
        self.state = { #state Identifiers
            0: "idle",
            1: "move",
            2: "attack",
            }

    def die(self):
        if random.randint(1, 5) == 1 or 2: # 20% chance to drop loot
            self.loot(self.item)
        else:
            self.dungeon_grid[self.grid_y][self.grid_x] = self.previous_tile # reset previous tile

    def loot(self,item):
        item.spawn(self.grid_x,self.grid_y) # spawn item at enemy position

    def position(self, dx, dy):
        self.grid_x = dx # Update enemy grid x position
        self.grid_y = dy # Update enemy grid y position
        self.dungeon_grid[dy][dx] = 6 # Set enemy position on grid

class Item(): #Item Manager
    def __init__(self,stats,dungeon_grid):
        self.type_name = ""
        self.stats = stats
        self.items = [] # Item List

    def spawn(self, sx, sy):
        self.generate_item(random.choice(["melee","ranged","consume"]))
        self.grid_x = sx # Update item grid x position
        self.grid_y = sy # Update item grid y position
        self.dungeon_grid[sy][sx] = 7 # Set item position on grid

    def generate_item(self,item_type):
        if item_type == "melee":
            self.type_name = random.choice(["sword","axe","dagger"])
            self.stats["numeric"] = random.randint(3, 10)
            self.stats["range"] = random.randint(1, 2)
            self.stats["radius"] = 0
            self.stats["effect"] = random.choice(["","bleed","stun","poison"])
        elif item_type == "ranged":
            self.type_name = random.choice(["bow","staff","tome"])
            self.stats["numeric"] = random.randint(1, 5)
            self.stats["range"] = random.randint(5, 10)
            self.stats["radius"] = random.randint(0, 1)
            self.stats["effect"] = random.choice(["","stun","weaken","poison"])
        elif item_type == "consume":
            self.type_name = random.choice(["potion"])
            self.stats["numeric"] = random.randint(5, 10)
            self.stats["range"] = 0
            self.stats["radius"] = 0
            self.stats["effect"] = random.choice(["healing","strength","poison","sleep"])
        if self.stats["effect"] == "":
            self.stats["price"] = (self.stats["numeric"] * 10 + self.stats["radius"] * 5 + self.stats["range"] * 2) + random.randint(-20, 20)
        else:
            self.stats["price"] = (self.stats["numeric"] * 10 + self.stats["radius"] * 5 + self.stats["range"] * 2) + random.randint(-10, 30)

        if self.stats["effect"] == "":
            self.stats["name"] = f"{self.type_name.capitalize()}"
        else:
            self.stats["name"] = f"{self.type_name.capitalize()} of {self.stats['effect'].capitalize()}"
        self.items.append(self.stats)

class Dungeon(): #Dungeon Manager
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.rooms = [] # Room List

    def reset(self): # Reset the dungeon
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)] # Clear grid
        self.rooms.clear() # Clear room list
        self.generate(random.randint(100, 150)) # Regenerate dungeon

    def add_room(self, x, y, w, h): # Add a room to the dungeon
        if x + w >= self.cols or y + h >= self.rows: # Make sure room fits
            return False

        for ry, rx, rh, rw in self.rooms: # Check for overlap
            if (x < rx + rw and x + w > rx and y < ry + rh and y + h > ry):
                return False

        for row in range(y, y + h): # Add room to grid
            for col in range(x, x + w):
                self.grid[row][col] = random.randint(1, 2) # Set floor tile

        self.rooms.append((y, x, h, w)) # Store room
        return True

    def add_walls(self, x, y, w, h): # Add walls around rooms
        for row in range(y - 1, y + h + 1): # Define wall hieght
            for col in range(x - 1, x + w + 1): # Define wall width
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    if self.grid[row][col] == 0:  # Only replace set tiles
                        self.grid[row][col] = random.randint(3,4) # Set wall tile
                    elif self.grid[row][col] in (3, 4): # If wall already exists
                        self.grid[row][col] = random.randint(1,2)  # floor tile

    def add_corridors(self, start_x, start_y, end_x, end_y): # add corridors between rooms
        if start_y == end_y: # Horizontal corridor
            for col in range(min(start_x, end_x), max(start_x, end_x) + 1): # Ensure the corridor moves horizontally
                self.grid[start_y][col] = random.randint(1, 2)  # Floor tile

        elif start_x == end_x:# Vertical corridor
            for row in range(min(start_y, end_y), max(start_y, end_y) + 1):# Ensure the corridor moves vertically
                self.grid[row][start_x] = random.randint(1, 2)  # Floor tile

    def generate(self, num_rooms, min_size=3, max_size=15): # Generate dungeon with rooms
        for _ in range(num_rooms): # Try to add rooms
            w = random.randint(min_size, max_size) # Random width
            h = random.randint(min_size, max_size) # Random height
            x = random.randint(1, self.cols - w - 1) # Random x position
            y = random.randint(1, self.rows - h - 1) # Random y position
            self.add_room(x, y, w, h) # Attempt to add room using values
           
        for (y, x, h, w) in self.rooms: # Add walls around rooms
            self.add_walls(x, y, w, h) # Attempt to add walls

        for i in range(1, len(self.rooms)): # Connect rooms with corridors
            y, x, h, w = self.rooms[i]
            ty, tx, th, tw = self.rooms[i - 1]
            self.add_corridors(x + w // 2, y + h // 2, tx + tw // 2, ty + th // 2)

    def place_player(self):
        if not self.rooms:
            return None
   
        y, x, h, w = self.rooms[0] # Choose the center of the first room as spawn
        spawn_x = x + w // 2
        spawn_y = y + h // 2

        return (spawn_x, spawn_y)

    def place_enemy(self):
        if not self.rooms:
            return None
   
        y, x, h, w = self.rooms[0] # Choose the center of the first room as spawn
        spawn_x = x + w // 2 + 1
        spawn_y = y + h // 2 + 1

        return (spawn_x, spawn_y)

def main(): #Game Loop
    game = True

    dungeon = Dungeon(rows, cols)
    player = Player(0, 0, cell_size, dungeon.grid)
    item = Item(stats,dungeon.grid)
    enemy = Enemy(0, 0, cell_size, dungeon.grid,item)
    camera = Camera(800, 600)

    dungeon.generate(random.randint(100, 150)) # Generate dungeon with random number of rooms

    spawn = dungeon.place_player() # Place player in dungeon
    enemy_spawn = dungeon.place_enemy() # Place enemy in dungeon

    player.position(spawn[0], spawn[1]) # Set player position on grid
    enemy.position(enemy_spawn[0], enemy_spawn[1]) # Set enemy position on grid

    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
        screen.fill((0, 0, 0))

        for row in range(rows): # Draw the grid
            for col in range(cols):
                value = dungeon.grid[row][col] # Asign Color
                rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                rect = camera.grid_to_screen(rect) # Camera
                pygame.draw.rect(screen, tiles[value], rect) # Color
                pygame.draw.rect(screen, (30, 30, 30), rect, 1) # Grid


        #Code Start

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: # Move Left
                    player.move(-1, 0)
                if event.key == pygame.K_RIGHT: # Move Right
                    player.move(1, 0)
                if event.key == pygame.K_UP: # Move Up
                    player.move(0, -1)
                if event.key == pygame.K_DOWN: # Move Down
                    player.move(0, 1)
                if event.key == pygame.K_ESCAPE: # Quit Game
                    game = False

        camera.center_on(player.camera_position())

        #Code End

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()