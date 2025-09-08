import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT)) #Window Setup
pygame.display.set_caption("Frouge")

cell_size = 10
cols, rows = 80, 60

tiles = { #Tile Identifiers
    0: (30, 30, 30),#Void
    1: (50, 50, 50),#Floor
    2: (100, 100, 100),#Wall
    3: (50, 200, 50),#Player
    4: (200, 50, 50),#Enemy
    5 : (50, 50, 200),#Loot
}

class Player(): #Player Manager
    def __init__(self, grid_x, grid_y, cell_size):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_size = cell_size

class Enemy(): #Enemy Manager
    print ("enemy")

class Item(): #Item Manager
    print ("item")

class Dungeon(): #Dungeon Manager
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.rooms = [] # Room List

    def add_room(self, x, y, w, h): # Add a room to the dungeon
        if x + w >= self.cols or y + h >= self.rows: # Make sure room fits
            return False

        for ry, rx, rh, rw in self.rooms: # Check for overlap
            if (x < rx + rw and x + w > rx and
                y < ry + rh and y + h > ry):
                return False

        for row in range(y, y + h): # Add room to grid
            for col in range(x, x + w):
                self.grid[row][col] = 1

        self.rooms.append((y, x, h, w)) # Store room
        return True

    def add_walls(self, x, y, w, h): # Add walls around rooms
        for row in range(y - 1, y + h + 1): # Define wall hieght
            for col in range(x - 1, x + w + 1): # Define wall width
                if (0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] == 0): # Check if empty
                    self.grid[row][col] = 2 # Set wall tile

    def generate(self, num_rooms, min_size=3, max_size=15): # Generate dungeon with rooms
        for _ in range(num_rooms): # Try to add rooms
            w = random.randint(min_size, max_size) # Random width
            h = random.randint(min_size, max_size) # Random height
            x = random.randint(1, self.cols - w - 1) # Random x position
            y = random.randint(1, self.rows - h - 1) # Random y position
            self.add_room(x, y, w, h) # Attempt to add room using values
            
        for (y, x, h, w) in self.rooms: # Add walls around rooms
            self.add_walls(x, y, w, h) # Attempt to add walls

        print ("Rooms Loaded")

    def place_player(self):
        if not self.rooms:
            return None
    
        y, x, h, w = self.rooms[0] # Choose the center of the first room as spawn
        spawn_x = x + w // 2
        spawn_y = y + h // 2

        self.grid[spawn_y][spawn_x] = 3  # Set player position
        return (spawn_x, spawn_y)

def main(): #Game Loop
    game = True

    dungeon = Dungeon(rows, cols)
    dungeon.generate(random.randint(50, 150)) # Generate dungeon with random number of rooms

    spawn = dungeon.place_player() # Place player in dungeon
    player = Player(spawn[0], spawn[1], cell_size)

    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
        screen.fill((0, 0, 0))

        #Code Start

        for row in range(rows): # Draw the grid
            for col in range(cols):
                value = dungeon.grid[row][col]
                rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, tiles[value], rect)
                pygame.draw.rect(screen, (30, 30, 30), rect, 1)

        #Code End

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()