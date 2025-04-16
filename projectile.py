from raylibpy import *

class Projectile:
  def __init__(self, x, y, r, dir):
    self.x = x
    self.y = y
    self.r = r
    self.dir = dir
    self.spd = 600

  def update(self):
    self.x += self.spd * self.dir.x * get_frame_time()
    self.y += self.spd * self.dir.y * get_frame_time()

  def draw(self):
    x = self.x + (1/2*self.r)
    y = self.y + (1/2*self.r)

    draw_circle(x, y, self.r, RED)



