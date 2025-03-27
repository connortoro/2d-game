from raylibpy import *
from enemy import Enemy
from animation import Animation, REPEATING, ONESHOT
from npc import NPC
import textures

class Room:
    empty_grid = None 
    scale = 100
    tile_size = 16

    tile_key = {
        'tl': (9, 2),
        't': (5, 2),
        'tr': (8, 2),
        'l': (6, 1),
        'r': (4, 1),
        'bl': (9, 1),
        'br': (8, 1),
        'o': (1, 1),
        'b': (5, 0),
        'x': (2, 3),
        's': (7, 1),
        'itl': (0, 0),
        'itr': (2 ,0),
        'it': (1,0),
        'il': (0, 1),
        'ir': (2, 1),
    }

    door_key = {
        'N': (10, 4),
        'S': (10, 4),
        'E': (5, 1),
        'W': (5, 1)
    }

    door_dest = {
        'N': (6, 0),
        'S': (6, 7),
        'E': (12, 3),
        'W': (0, 3)
    }

    # Initializes floor texture and empty grid once
    @classmethod
    def initialize(cls):
        if cls.empty_grid is None:
            cls.empty_grid = [
                ["tl", "t", "t", "t", "t", "t", "t", "t", "t", "t", "t", "t", "tr"],
                ["l",  "itl", "it", "it", "it", "it", "it", "it", "it", "it", "it", "itr", "r"],
                ["l",  "il", "o", "o", "o", "o", "o", "o", "o", "o", "o", "ir", "r"],
                ["l",  "il", "o", "o", "o", "o", "o", "o", "o", "o", "o", "ir", "r"],
                ["l",  "il", "o", "o", "o", "o", "o", "o", "o", "o", "o", "ir", "r"],
                ["l",  "il", "o", "o", "o", "o", "o", "o", "o", "o", "o", "ir", "r"],
                ["l",  "il", "o", "o", "o", "o", "o", "o", "o", "o", "o", "ir", "r"],
                ["bl", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "br"]
            ]

    def __init__(self, obstacles_path, enemies_path, door_string):
        if Room.empty_grid is None:
            Room.initialize()

        self.door_string = door_string
        self.doors = []
        self.rectangles = []
        self.spikes = []
        self.objects = []

        self.obstacle_grid = []
        with open(obstacles_path) as file:
            for line in file:
                self.obstacle_grid.append(line.strip().split(" "))
        self.gen_rectangles()

        self.enemies = []
        self.enemy_grid = []
        with open(enemies_path) as file:
            for line in file:
                self.enemy_grid.append(line.strip().split())
        self.gen_enemies()

    def update(self, player):
        self.update_enemies(player)
        self.update_objects(player)

    def draw(self):
        self.draw_empty_room()
        self.draw_doors()
        self.draw_obstacles()
        self.draw_enemies()
        self.draw_objects()

    def update_enemies(self, player):
        for enemy in self.enemies:
            enemy.update(player, self.rectangles, self)
    
    def update_objects(self, player):
        for object in self.objects:
            object.update(player, self)

    def draw_objects(self):
        for object in self.objects:
            object.draw()
      
    def draw_empty_room(self):
        for dest_y, row in enumerate(self.empty_grid):
            for dest_x, tile_char in enumerate(row):
                source_x, source_y = self.tile_key[tile_char]
                source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
                dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale, self.scale, self.scale)
                draw_texture_pro(textures.room_texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)

    def draw_obstacles(self):
        for dest_y, row in enumerate(self.obstacle_grid):
            for dest_x, tile_char in enumerate(row):
                if tile_char == 'o': continue
                source_x, source_y = self.tile_key[tile_char]
                source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
                dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale, self.scale, self.scale)
                draw_texture_pro(textures.old_room_texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)
  
    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()
        
    def draw_doors(self):
        for dir in self.door_string:
            source_x, source_y = self.door_key[dir]
            dest_x, dest_y = self.door_dest[dir]

            source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
            dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale,self.scale, self.scale)
            draw_texture_pro(textures.room_texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)
          
    def gen_rectangles(self):
        for y, row in enumerate(self.obstacle_grid):
            for x, tile_char in enumerate(row):
                if tile_char == 's':
                    rect = Rectangle(x * self.scale, y * self.scale, self.scale, self.scale)
                    self.spikes.append(rect)
                elif not tile_char == 'o':
                    rect = Rectangle(x * self.scale, y * self.scale, self.scale, self.scale)
                    self.rectangles.append(rect)
        for dir in self.door_string:
            x, y = self.door_dest[dir]
            self.doors.append(Rectangle(x*self.scale , y*self.scale , self.scale, self.scale))

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

                if tile_char == 't':
                    texture = load_texture("assets/player_sheet/8d-character.png")
                    self.objects.append(NPC(texture, x*self.scale, y*self.scale))
