from raylibpy import *
from animation import Animation, REPEATING

class Enemy:
    W = 32
    H = 32
    SCALE = 4

    def __init__(self, sheet, x, y):
        self.sheet = load_texture(sheet)
        self.vel = Vector2(0.0, 0.0)
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.animation = Animation(0, 3, 1, 0, 0.2, 0.2, REPEATING, 32, 32)
        self.hitbox = Rectangle(
            self.rect.x + (self.rect.width - 90) / 2,  # Center horizontally
            self.rect.y + self.rect.height - 60,      # Position at bottom of sprite
            90,
            60
        )

    def update(self):
        self.animation.animation_update()

    def draw(self):
        source = self.animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.sheet, source, self.rect, origin, 0.0, WHITE)
        draw_rectangle_lines_ex(self.hitbox, 1, RED) 


