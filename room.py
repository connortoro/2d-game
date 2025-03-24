from raylibpy import *
from enemy import Enemy
from animation import Animation, REPEATING, ONESHOT
from npc import NPC

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
        'x': (2, 3),
        's': (7, 1),
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

    def __init__(self, obstacles_path, enemies_path, npcs_path, door_string, is_trader_room=False):
        if Room.texture is None:
            Room.initialize()

        self.door_string = door_string
        self.is_trader_room = is_trader_room
        self.doors = []
        self.rectangles = []
        self.spikes = []
        self.object_grid = []
        self.npcs = []
        self.npc_grid = []
        with open(obstacles_path) as file:
            for line in file:
                self.object_grid.append(line.strip().split(" "))
        self.gen_rectangles()
        
        with open(npcs_path) as file:
            for line in file:
                self.npc_grid.append(line.strip().split())
        self.gen_npcs()

        self.enemies = []
        self.enemy_grid = []
        with open(enemies_path) as file:
            for line in file:
                self.enemy_grid.append(line.strip().split())
        self.gen_enemies()

    def update(self, player):
        for enemy in self.enemies:
            enemy.update(player, self.rectangles)
        self.check_npc_interaction(player)

    def draw(self):
        self.draw_empty_room()
        self.draw_doors()
        self.draw_objects()
        self.draw_enemies()
        self.draw_npcs()
      
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

    def draw_npcs(self):
        for npc in self.npcs:
            npc.draw()
        
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
                if tile_char == 's':
                    rect = Rectangle(x * self.scale, y * self.scale, self.scale, self.scale)
                    self.spikes.append(rect)
        for dir in self.door_string:
            x, y = self.door_dest[dir]
            if dir == "N" or dir == "S":
                x += .3
                self.doors.append(Rectangle(x*self.scale - 10, y*self.scale + 30, 40, 40))
            else:
                self.doors.append(Rectangle(x*self.scale - 10, y*self.scale + 30, 40, 80))

    def gen_enemies(self):
        for y, row in enumerate(self.enemy_grid):
            for x, tile_char in enumerate(row):

                if tile_char == '1':
                    animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                    death_animation = Animation(0, 5, 1, 8, 16, .2, .2, ONESHOT, 32, 32)
                    enemy = Enemy("assets/enemy_sheets/LV1_BOSS.png", x * self.scale, y * self.scale, 70, 120, 30, animation, death_animation)
                    self.enemies.append(enemy)

                if tile_char == '2':
                    animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                    death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                    enemy = Enemy("assets/enemy_sheets/MINION_1.png", x * self.scale, y * self.scale, 20, 200, 8, animation, death_animation)
                    self.enemies.append(enemy)

                if tile_char == '3':
                    animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                    death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                    enemy = Enemy("assets/enemy_sheets/MINION_3.png", x * self.scale, y * self.scale, 30, 135, 13, animation, death_animation)
                    self.enemies.append(enemy)

                if tile_char == '4':
                    animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                    death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                    enemy = Enemy("assets/enemy_sheets/MINION_4.png", x * self.scale, y * self.scale, 40, 110, 20, animation, death_animation)
                    self.enemies.append(enemy)

    def gen_npcs(self):
        self.npcs = []
        for y, row in enumerate(self.npc_grid):
            for x, tile_char in enumerate(row):
                if (tile_char == '2' and self.object_grid[y][x] == "t") or (self.is_trader_room and len(self.npcs) == 0):
                        center_x = x * self.scale + (self.scale - (16 * 5)) / 2 + 30
                        center_y = y * self.scale + (self.scale - (24 * 5)) / 2 + 30
                        npc = NPC(load_texture("assets/player_sheet/8d-character.png"), center_x, center_y)
                        self.npcs.append(npc)
    
    def check_npc_interaction(self, player):
        for npc in self.npcs:
            if (abs(player.rect.x - npc.x) < self.scale and
                abs(player.rect.y - npc.y) < self.scale):
                npc.check_interaction(player)