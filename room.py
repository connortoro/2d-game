from raylibpy import *
from enemy import Enemy
from animation import Animation, REPEATING, ONESHOT
from necro import Necro
from npc import NPC
import textures
import json
from config import *

class Room:

    door_key = {
        'N': (10, 4),
        'S': (10, 4),
        'E': (5, 1),
        'W': (5, 1)
    }

    door_dest = {
        'N': (7, 0),
        'S': (7, 8),
        'E': (14, 4),
        'W': (0, 4)
    }

    # Initializes floor texture and empty grid once

    def __init__(self, map, door_string):
        with open(map, 'r') as file:
            self.map = json.load(file)
        self.door_string = door_string

        self.doors = []
        self.rectangles = []
        self.spikes = []
        self.objects = []
        self.enemies = []
        self.color = Color(255, 200, 200, 255)

        self.gen()

    def update(self, player):
        self.update_enemies(player)
        self.update_objects(player)

    def update_enemies(self, player):
        for enemy in self.enemies:
            enemy.update(player, self.rectangles, self)

    def update_objects(self, player):
        for object in self.objects:
            object.update(player, self)

    def draw(self):
        self.draw_room()
        self.draw_doors()
        self.draw_enemies()
        self.draw_objects()

    def draw_room(self):
        for layer in self.map['layers']:
            if layer['type'] == 'tilelayer':
                for i, gid in enumerate(layer['data']):
                    if gid == 0: continue

                    dest_x = i % COLS
                    dest_y = i // COLS
                    dest_rect = Rectangle(dest_x*SCALE, dest_y*SCALE, SCALE, SCALE)

                    tileset, j = self.get_tileset_name(gid)

                    src_x = (j % textures.src_map[tileset]['width']) * TILE_SIZE
                    src_y = (j // textures.src_map[tileset]['width']) * TILE_SIZE
                    src_rect = Rectangle(src_x, src_y, TILE_SIZE, TILE_SIZE)

                    draw_texture_pro(textures.src_map[tileset]['texture'], src_rect, dest_rect, Vector2(0, 0), 0.0, self.color)

    def draw_objects(self):
        for object in self.objects:
            object.draw()

    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def draw_doors(self):
        for dir in self.door_string:
            dest_x, dest_y = self.door_dest[dir]
            source_rect = None
            if dir == 'N' or dir == 'S':
                source_rect = Rectangle(176, 176, TILE_SIZE, TILE_SIZE)
            else:
                source_rect = Rectangle(208, 144, TILE_SIZE, TILE_SIZE)
            dest_rect = Rectangle(dest_x * SCALE, dest_y * SCALE,SCALE, SCALE)
            draw_texture_pro(textures.base, source_rect, dest_rect, Vector2(0,0), 0, self.color)

    def gen(self):
        self.gen_enemies(self.map['layers'][2])
        self.gen_rectangles(self.map['layers'][1])
        self.gen_doors()

    def gen_rectangles(self, layer):
        for i, gid in enumerate(layer['data']):
            if gid == 0:
                continue
            else:
                x = (i % COLS) * SCALE
                y = (i // COLS) * SCALE
                self.rectangles.append(Rectangle(x, y, SCALE, SCALE))

    def gen_doors(self):
        for dir in self.door_string:
            x, y = self.door_dest[dir]
            self.doors.append(Rectangle((x*SCALE)-4 , (y*SCALE)-4 , SCALE+8, SCALE+8))

    def gen_enemies(self, layer):
        for entity in layer['objects']:
            x = entity['x'] * (SCALE / TILE_SIZE)
            y = entity['y'] * (SCALE / TILE_SIZE)

            if entity['name'] == 'zombie':
                animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                death_animation = Animation(0, 5, 1, 8, 16, .2, .2, ONESHOT, 32, 32)
                enemy = Enemy(textures.zombie, x , y , 70, 120, 30, animation, death_animation)
                self.enemies.append(enemy)

            elif entity['name'] == 'minion':
                animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                enemy = Enemy(textures.minion, x , y , 20, 200, 8, animation, death_animation)
                self.enemies.append(enemy)

            elif entity['name'] == 'mummy':
                animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                enemy = Enemy(textures.mummy, x, y, 30, 135, 13, animation, death_animation)
                self.enemies.append(enemy)

            elif entity['name'] == 'bat':
                animation = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                death_animation = Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)
                enemy = Enemy(textures.bat, x , y , 40, 110, 20, animation, death_animation)
                self.enemies.append(enemy)
            elif entity['name'] == 'necro':
                enemy = Necro(textures.necro, x, y)
                self.enemies.append(enemy)
            elif entity['name'] == 'trader':

                self.objects.append(NPC(x, y))

    def get_tileset_name(self, gid):
        for tileset in self.map['tilesets']:
            first_gid = tileset['firstgid']
            next_gid = (self.map['tilesets'][self.map['tilesets'].index(tileset) + 1]['firstgid']
                        if self.map['tilesets'].index(tileset) + 1 < len(self.map['tilesets'])
                        else float('inf'))

            if first_gid <= gid < next_gid:
                return (tileset['source'], gid-first_gid)
        return None

