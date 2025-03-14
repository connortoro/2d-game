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

    # Init
    def __init__(self, obstacles_path, enemies_path):
        if Room.texture is None:
            Room.initialize()  # Ensure initialization if not already done

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
          
    def gen_rectangles(self):
        for y, row in enumerate(self.object_grid):
            for x, tile_char in enumerate(row):
                if tile_char == 'x':
                    rect = Rectangle(x * self.scale, y * self.scale, self.scale, self.scale)
                    self.rectangles.append(rect)

    def gen_enemies(self):
        for y, row in enumerate(self.enemy_grid):
            for x, tile_char in enumerate(row):
                if tile_char == '1':
                    enemy = Enemy("assets/enemy_sheets/LV1_BOSS.png", x * self.scale, y * self.scale, 100)
                    self.enemies.append(enemy)