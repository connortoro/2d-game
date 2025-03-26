from raylibpy import *

class Heart:
    def __init__(self, x, y, texture):
        self.rect = Rectangle(x-25, y-25, 50, 50)
        self.texture = texture

    def update(self, player, room):
        if check_collision_recs(self.rect, player.hitbox):
            health_pickup = load_sound("assets/audio/health_pickup.mp3")
            play_sound(health_pickup)
            player.heal(10)
            room.objects.remove(self)

    def draw(self):
        draw_texture_pro(self.texture, Rectangle(13*16, 1*16, 16, 16), self.rect, Vector2(0, 0), 0, WHITE)