from raylibpy import *
import textures
from animation import Animation, REPEATING

class Projectile:
  def __init__(self, x, y, r, dir):
    self.center = Vector2(x, y)
    self.r = r
    self.dir = dir
    self.spd = 600
    self.dmg = 40
    self.active = True


    self.size = r*5
    self.animation = Animation(0, 6, 0, 0, 0, .15, .15, REPEATING, 32, 32)

  def update(self):
    if not self.active: return

    self.animation.animation_update()
    self.center.x += self.spd * self.dir.x * get_frame_time()
    self.center.y += self.spd * self.dir.y * get_frame_time()



  def draw(self):
    if not self.active: return
    #draw_circle(self.center.x, self.center.y, self.r, RED)
    dest = Rectangle(self.center.x-(.5*self.size), self.center.y-(.5*self.size), self.size, self.size)
    draw_texture_pro(textures.spark, self.animation.animation_frame_horizontal(), dest, Vector2(0,0), 0.0, RED)





