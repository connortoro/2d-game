from room import Room
from raylibpy import *

class Floor:
  def __init__(self):
    self.rooms = []
    self.gen()

  def gen(self):
    self.rooms.append(Room("assets/floors/two_blocks.txt"))

