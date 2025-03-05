from room import Room
from raylibpy import *

class Floor:
  def __init__(self):
    self.rooms = []
    self.gen()

  def gen(self):
    self.rooms.append(Room("assets/floors/1/obstacles.txt", "assets/floors/1/enemies.txt"))

