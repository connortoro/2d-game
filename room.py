from raylibpy import *
from enemy import Enemy
from animation import Animation, REPEATING, ONESHOT
from necro import Necro
from demon import Demon
from npc import NPC
from orc import Orc
from orc_dasher import OrcDasher
from orc_boss import OrcBoss
import random
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

    def __init__(self, map, door_string, floor, color, sound_manager):
        self.sound_manager = sound_manager
        with open(map, 'r') as file:
            self.map = json.load(file)
        self.door_string = door_string

        self.floor = floor
        self.doors = []
        self.rectangles = []
        self.spikes = []
        self.objects = []
        self.enemies = []
        self.color = color

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
        self.gen_enemies(self.map['layers']) # main enemy spawn
        #self.gen_test_enemy() # testing purposes 
        self.gen_rectangles(self.map['layers'])
        self.gen_spikes(self.map['layers'])
        self.gen_doors()
        

    def gen_spikes(self, layers):
        for layer in layers:
            if layer['name'] == 'spikes':
                for i, gid in enumerate(layer['data']):
                    if gid == 0:
                        continue
                    else:
                        x = (i % COLS) * SCALE
                        y = (i // COLS) * SCALE
                        self.spikes.append(Rectangle(x, y, SCALE, SCALE))

    def gen_rectangles(self, layers):
        for layer in layers:
            if layer['name'] == 'obstacles':
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

    def gen_enemies(self, layers):
        room_width = COLS * SCALE
        room_height = (len(self.map['layers'][0]['data']) // COLS) * SCALE

        for layer in layers:
            if layer['name'] == 'enemies':
                for entity in layer['objects']:
                    x = entity['x'] * (SCALE / TILE_SIZE)
                    y = entity['y'] * (SCALE / TILE_SIZE)

                    if entity['name'] == 'zombie':
                        idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                        death = Animation(0, 5, 1, 8, 16, 0.2, 0.2, ONESHOT, 32, 32)
                        animations = {"idle_front": idle, "death": death}
                        enemy = Enemy(textures.zombie, x, y, 70, 120, 30, animations, death, room_width, room_height, self.sound_manager, use_melee_attack=False)
                        self.enemies.append(enemy)

                    elif entity['name'] == 'minion':
                        idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                        death = Animation(0, 4, 1, 10, 16, 0.2, 0.2, ONESHOT, 32, 32)
                        animations = {"idle_front": idle, "death": death}
                        enemy = Enemy(textures.minion, x, y, 20, 200, 8, animations, death, room_width, room_height, self.sound_manager, use_melee_attack=False)
                        self.enemies.append(enemy)

                    elif entity['name'] == 'mummy':
                        idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                        death = Animation(0, 4, 1, 10, 16, 0.2, 0.2, ONESHOT, 32, 32)
                        animations = {"idle_front": idle, "death": death}
                        enemy = Enemy(textures.mummy, x, y, 30, 135, 13, animations, death, room_width, room_height, self.sound_manager, use_melee_attack=False)
                        self.enemies.append(enemy)

                    elif entity['name'] == 'bat':
                        idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
                        death = Animation(0, 4, 1, 10, 16, 0.2, 0.2, ONESHOT, 32, 32)
                        animations = {"idle_front": idle, "death": death}
                        enemy = Enemy(textures.bat, x, y, 40, 110, 20, animations, death, room_width, room_height, self.sound_manager, use_melee_attack=False)
                        self.enemies.append(enemy)
                    elif entity['name'] == 'orc':
                        enemy = Orc(textures.orc1, x, y, room_width, room_height)
                        self.enemies.append(enemy)

                    elif entity['name'] == 'orc_dasher':
                        enemy = OrcDasher(textures.orc2, x, y, room_width, room_height)
                        self.enemies.append(enemy)

                    elif entity['name'] == 'boss':
                        r = random.random()
                        if r < 1/3:
                            enemy = Demon(textures.demon, x, y, self, self.sound_manager)
                        elif r < 2/3:
                            enemy = OrcBoss(textures.orc3, x, y, room_width, room_height)
                        else:
                            enemy = Necro(textures.necro, x, y, self, self.sound_manager)
                        self.enemies.append(enemy)


                    elif entity['name'] == 'trader':
                        self.objects.append(NPC(x - 50, y + -100))

    def get_tileset_name(self, gid):
        for tileset in self.map['tilesets']:
            first_gid = tileset['firstgid']
            next_gid = (self.map['tilesets'][self.map['tilesets'].index(tileset) + 1]['firstgid']
                        if self.map['tilesets'].index(tileset) + 1 < len(self.map['tilesets'])
                        else float('inf'))

            if first_gid <= gid < next_gid:
                return (tileset['source'], gid-first_gid)
        return None

    def gen_test_enemy(self):
        room_width = COLS * SCALE
        room_height = (len(self.map['layers'][0]['data']) // COLS) * SCALE

        # Choose a fixed location to spawn
        x = 500
        y = 300

        # === Swap any of these blocks to test different enemies ===

        # --- Test zombie ---
        #idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
        #death = Animation(0, 5, 1, 8, 16, 0.2, 0.2, ONESHOT, 32, 32)
        #animations = {"idle_front": idle, "death": death}
        #enemy = Enemy(textures.zombie, x, y, 70, 120, 30, animations, death, room_width, room_height, self.sound_manager)
        #self.enemies.append(enemy)

        # --- Test Demon ---
        #enemy = Demon(textures.demon, x, y, self, self.sound_manager)
        #self.enemies.append(enemy)

        # # --- Test Necro ---
        # necro = Necro(textures.necro, x, y, self, self.sound_manager)
        # self.enemies.append(necro)

        # # --- Test Minion ---
        # idle = Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32)
        # death = Animation(0, 4, 1, 10, 16, 0.2, 0.2, ONESHOT, 32, 32)
        # animations = {"idle_front": idle, "death": death}
        # minion = Enemy(textures.minion, x, y, 20, 200, 8, animations, death, room_width, room_height, self.sound_manager)
        # self.enemies.append(minion)

        # --- Test OrcBoss ---
        # orc_boss = OrcBoss(textures.orc3, x, y, room_width, room_height)
        # orc_boss.health = orc_boss.maxHealth // 2
        # self.enemies.append(orc_boss)
