import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Window Setup
pygame.display.set_caption("Frogue")

cell_size = 35
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

    def move(self, dx, dy):
        if self.dungeon_grid[self.grid_y + dy][self.grid_x + dx] in (1, 2):
            self.dungeon_grid[self.grid_y][self.grid_x] = self.previous_tile # reset previous tile
            self.grid_x += dx # new x
            self.grid_y += dy # new y
            self.previous_tile = self.dungeon_grid[self.grid_y][self.grid_x] # store new previous tile
            self.position(self.grid_x, self.grid_y) # move player

class Enemy(): #Enemy Manager
    def __init__(self, state):
        self.state = state

class Item(): #Item Manager
    def __init__(self, item_type):
        self.item_type = item_type

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
                    if self.grid[row][col] == 0:  # Only replace empty space
                        self.grid[row][col] = random.randint(3, 4) # Set wall tile
                    elif self.grid[row][col] in (3, 4): # If wall already exists
                        self.grid[row][col] = random.randint(1,2)  # floor tile

    def generate(self, num_rooms, min_size=3, max_size=15): # Generate dungeon with rooms
        for _ in range(num_rooms): # Try to add rooms
            w = random.randint(min_size, max_size) # Random width
            h = random.randint(min_size, max_size) # Random height
            x = random.randint(1, self.cols - w - 1) # Random x position
            y = random.randint(1, self.rows - h - 1) # Random y position
            self.add_room(x, y, w, h) # Attempt to add room using values
           
        for (y, x, h, w) in self.rooms: # Add walls around rooms
            self.add_walls(x, y, w, h) # Attempt to add walls

    def place_player(self):
        if not self.rooms:
            return None
   
        y, x, h, w = self.rooms[0] # Choose the center of the first room as spawn
        spawn_x = x + w // 2
        spawn_y = y + h // 2

        return (spawn_x, spawn_y)

def main(): #Game Loop
    game = True

    dungeon = Dungeon(rows, cols)
    player = Player(0, 0, cell_size, dungeon.grid)
    camera = Camera(800, 600)

    dungeon.generate(random.randint(100, 150)) # Generate dungeon with random number of rooms

    spawn = dungeon.place_player() # Place player in dungeon

    player.position(spawn[0], spawn[1]) # Set player position on grid

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