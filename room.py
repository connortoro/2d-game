from raylibpy import *
from enemy import Enemy

class Room:
    texture = None
    empty_grid = None 
    scale = 100
    tile_size = 16

    tile_key = {
        'tl': (0, 0),
        't': (1, 0),
        'tr': (3, 0),
        'l': (0, 1),
        'r': (9, 1),
        'bl': (0, 4),
        'br': (3, 4),
        'o': (1, 1),
        'b': (1, 4),
        'x': (2, 3)
    }

    door_key = {
        'N': (7, 0),
        'S': (7, 0),
        'E': (9, 0),
        'W': (9, 0)
    }

    door_dest = {
        'N': (6, -.2),
        'S': (6, 6.7),
        'E': (12.6, 3.3),
        'W': (.25, 3.3)
    }

    # Initializes floor texture and empty grid once
    @classmethod
    def initialize(cls):
        if cls.texture is None:
            cls.texture = load_texture("assets/textures/tileset_blue.png")
        if cls.empty_grid is None:
            cls.empty_grid = [
                ["tl", "t", "t", "t", "t", "t", "t", "t", "t", "t", "t", "t", "tr"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["l",  "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "r"],
                ["bl", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "br"]
            ]

    def __init__(self, obstacles_path, enemies_path, door_string):
        if Room.texture is None:
            Room.initialize()

        self.door_string = door_string
        self.doors = []
        self.rectangles = []
        self.object_grid = []
        with open(obstacles_path) as file:
            for line in file:
                self.object_grid.append(line.strip().split(" "))
        self.gen_rectangles()
        
        self.enemies = []
        self.enemy_grid = []
        with open(enemies_path) as file:
            for line in file:
                self.enemy_grid.append(line.strip().split())
        self.gen_enemies()

    def update(self, player):
        for enemy in self.enemies:
            enemy.update(player, self.rectangles)

    def draw(self):
        self.draw_empty_room()
        self.draw_doors()
        self.draw_objects()
        self.draw_enemies()
      
    def draw_empty_room(self):
        for dest_y, row in enumerate(self.empty_grid):
            for dest_x, tile_char in enumerate(row):
                source_x, source_y = self.tile_key[tile_char]
                source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
                dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale, self.scale, self.scale)
                draw_texture_pro(self.texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)

    def draw_objects(self):
        for dest_y, row in enumerate(self.object_grid):
            for dest_x, tile_char in enumerate(row):
                if tile_char == 'o': continue
                source_x, source_y = self.tile_key[tile_char]
                source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
                dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale, self.scale, self.scale)
                draw_texture_pro(self.texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)
  
    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def draw_doors(self):
        for dir in self.door_string:
            source_x, source_y = self.door_key[dir]
            dest_x, dest_y = self.door_dest[dir]

            source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
            dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale,self.scale, self.scale)
            draw_texture_pro(self.texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)
          
    def gen_rectangles(self):
        for y, row in enumerate(self.object_grid):
            for x, tile_char in enumerate(row):
                if tile_char == 'x':
                    rect = Rectangle(x * self.scale, y * self.scale, self.scale, self.scale)
                    self.rectangles.append(rect)
        for dir in self.door_string:
            x, y = self.door_dest[dir]
            if dir == "N" or dir == "S":
                x += .3
            self.doors.append(Rectangle(x*self.scale - 10, y*self.scale + 30, 40, 40))

    def gen_enemies(self):
        for y, row in enumerate(self.enemy_grid):
            for x, tile_char in enumerate(row):
                if tile_char == '1':
                    enemy = Enemy("assets/enemy_sheets/LV1_BOSS.png", x * self.scale, y * self.scale, 100)
                    self.enemies.append(enemy)