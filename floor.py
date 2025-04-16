from room import Room
from player import Player
import random
from raylibpy import *
from config import *

class Floor:
  NUM_FLOORS = 1 #TODO CHANGE AS FLOORS & ROOMS ARE ADDED
  NUM_ROOMS = 5

  def __init__(self):
    self.rooms = []
    self.pos = (3, 2)
    self.map = [['x'] * 10 for _ in range(6)]
    self.map[3][2] = 'o'
    self.gen()

  def update(self, player):
    y, x = self.pos
    self.rooms[y][x].update(player)
    self.door_check(player)

  def draw(self):
    y, x = self.pos
    self.rooms[y][x].draw()

  def get_current_room(self):
    y, x = self.pos
    return self.rooms[y][x]

  def gen(self):
    floor_num = random.randint(1, self.NUM_FLOORS)
    with open(f"assets/floors/{str(floor_num)}.txt") as file:
      for line in file:
        self.rooms.append(line.strip().split(" "))
    for y, row in enumerate(self.rooms):
      for x, tile_char in enumerate(row):
        if tile_char == "o":
          room_num = 6#str(random.randint(1, self.NUM_ROOMS))
          door_string = self.get_door_string(y, x)
          self.rooms[y][x] = Room(f"tiles/{room_num}.json", door_string)
        elif tile_char == 's':
          door_string = self.get_door_string(y, x)
          self.rooms[y][x] = Room("tiles/0.json", door_string)


  def get_door_string(self, y, x):
    res = ""
    if self.rooms[y-1][x] != "x":
      res += "N"
    if self.rooms[y][x+1] != "x":
      res += "E"
    if self.rooms[y+1][x] != "x":
      res += "S"
    if self.rooms[y][x-1] != "x":
      res += "W"
    return res

  def door_check(self, player: Player):
    room: Room = self.get_current_room()
    for enemy in room.enemies:
      if enemy.is_alive:
        return

    for door in room.doors:
      if check_collision_recs(player.hitbox, door):
        if player.rect.y < 100: # N
          y, x = self.pos
          self.pos = (y-1, x)
          self.map[y-1][x] = 'o'
          player.rect.y = SCALE*5.8
        elif player.rect.y > 500: # S
          y, x = self.pos
          self.pos = (y+1, x)
          self.map[y+1][x] = 'o'
          player.rect.y = SCALE
        elif player.rect.x < 200:
          y, x = self.pos
          self.pos = (y, x-1)
          self.map[y][x-1] = 'o'
          player.rect.x = 1110
        else:
          y, x = self.pos
          self.pos = (y, x+1)
          self.map[y][x+1] = 'o'
          player.rect.x = 100
