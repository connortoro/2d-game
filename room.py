from raylibpy import *

class Room:
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
    'b': (1, 4)
  }

  # This makes sure the texture is only once
  texture = None
  @classmethod
  def initialize(cls):
      if cls.texture is None:
          cls.texture = load_texture("assets/textures/tileset_blue.png")

  def __init__(self, grid):
    if Room.texture is None:
      Room.initialize()
    self.grid = grid

  def draw(self):
    for dest_y, row in enumerate(self.grid):
      for dest_x, tile_char in enumerate(row):
        source_x, source_y = self.tile_key[tile_char]
        source_rect = Rectangle(source_x * self.tile_size, source_y * self.tile_size, self.tile_size, self.tile_size)
        dest_rect = Rectangle(dest_x * self.scale, dest_y * self.scale, self.scale, self.scale)
        draw_texture_pro(self.texture, source_rect, dest_rect, Vector2(0,0), 0, WHITE)

    





