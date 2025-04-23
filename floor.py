from room import Room
from player import Player
import random
from raylibpy import *
from config import *

class Floor:
    NUM_FLOORS = 1  # TODO CHANGE AS FLOORS & ROOMS ARE ADDED
    NUM_ROOMS = 5

    def __init__(self):
        self.rooms = []
        self.pos = (3, 2)
        self.map = [['x'] * 10 for _ in range(6)]
        self.map[3][2] = 'o'
        self.gen()

    def update(self, player: Player):
        y, x = self.pos
        self.rooms[y][x].update(player)
        self.door_check(player)

    def draw(self):
        y, x = self.pos
        self.rooms[y][x].draw()

    def get_current_room(self) -> Room:
        y, x = self.pos
        return self.rooms[y][x]

    def gen(self):
        floor_num = random.randint(1, self.NUM_FLOORS)
        with open(f"assets/floors/{floor_num}.txt") as file:
            for line in file:
                self.rooms.append(line.strip().split(" "))
        for y, row in enumerate(self.rooms):
            for x, tile_char in enumerate(row):
                door_string = self.get_door_string(y, x)
                if tile_char == "o":
                    room_num = random.randint(1, self.NUM_ROOMS)
                    self.rooms[y][x] = Room(f"tiles/{room_num}.json", door_string)
                elif tile_char == "s":
                    self.rooms[y][x] = Room("tiles/0.json", door_string)
                elif tile_char == 'b':
                    self.rooms[y][x] = Room("tiles/b.json", door_string)

    def get_door_string(self, y: int, x: int) -> str:
        res = ""
        if y > 0 and self.rooms[y-1][x] != "x":
            res += "N"
        if x < len(self.rooms[0]) - 1 and self.rooms[y][x+1] != "x":
            res += "E"
        if y < len(self.rooms) - 1 and self.rooms[y+1][x] != "x":
            res += "S"
        if x > 0 and self.rooms[y][x-1] != "x":
            res += "W"
        return res

    def door_check(self, player: Player):
        room = self.get_current_room()

        # Only allow room change if all enemies are dead
        for enemy in room.enemies:
            if enemy.is_alive:
                return

        # Check each door rect for collision
        for door in room.doors:
            if check_collision_recs(player.hitbox, door):

                y, x = self.pos
                # Determine which door was hit by player's position
                if player.rect.y < 100:  # North door
                    self.pos = (y-1, x)
                    self.map[y-1][x] = 'o'
                    player.rect.y = SCALE * 5.8
                elif player.rect.y > 500:  # South door
                    self.pos = (y+1, x)
                    self.map[y+1][x] = 'o'
                    player.rect.y = SCALE
                elif player.rect.x < 200:  # West door
                    self.pos = (y, x-1)
                    self.map[y][x-1] = 'o'
                    player.rect.x = 1110
                else:  # East door
                    self.pos = (y, x+1)
                    self.map[y][x+1] = 'o'
                    player.rect.x = 100
                break
