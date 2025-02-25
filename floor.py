from room import Room
from raylibpy import *

class Floor:
  def __init__(self):
    self.rooms = []
    self.gen()

  def gen(self):
    grid = []
    with open("assets/floors/empty.txt") as file:
      for line in file:
        grid.append(line.strip().split(" "))
    self.rooms.append(Room(grid))

