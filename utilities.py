from raylibpy import *

def center_of_rect(rect: Rectangle):
  cx = rect.x + (rect.width/2.0)
  cy = rect.y + (rect.height/2.0)
  return Vector2(cx, cy)

def direction_between_rects(a: Rectangle, b: Rectangle):
  va = center_of_rect(a)
  vb = center_of_rect(b)
  return vector2_normalize(vector2_subtract(vb, va))
