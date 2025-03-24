from raylibpy import *
from animation import Animation, REPEATING

W = 1300
H = 900


class NPC:
    def __init__(self, texture, x, y):
        sprite_width = 16 * 5
        sprite_height = 24 * 5
        self.x = x
        self.y = y
        self.texture = texture
        self.rect = Rectangle(x, y, sprite_width, sprite_height)
        self.current_animation = Animation(1, 3, 1, 8, 24, 0.1, 0.1, REPEATING, 16, 24)
        self.interacted = False
        self.dialog_options = {
            1: "Increase Health",
            2: "Increase Speed",
            3: "Increase Attack"
        }

    def draw(self):
        source = self.current_animation.animation_frame_vertical()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.texture, source, self.rect, origin, 0.0, WHITE)

    def check_interaction(self, player):
        if check_collision_recs(self.rect, player.rect):
            draw_text("Press [E] to interact", int(self.rect.x), int(self.rect.y - 20), 20, WHITE)
        if is_key_pressed(KEY_E) and not player.in_dialog:
            self.show_dialog(player)
    
    def show_dialog(self, player):
        player.in_dialog = True
        player.dialog_npc = self
        