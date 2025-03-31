from raylibpy import *

class Menu:
    def __init__(self):
        self.options = ["Resume", "Quit"]
        self.selected_index = 0
        self.font_size = 40
        self.spacing = 10
        self.active_color = RED
        self.inactive_color = WHITE

    def draw(self, screen_width, screen_height):
        for i, option in enumerate(self.options):
            color = self.active_color if i == self.selected_index else self.inactive_color
            text_width = measure_text(option, self.font_size)
            position_x = (screen_width - text_width) // 2
            position_y = (screen_height // 2) + i * (self.font_size + self.spacing)
            draw_text(option, position_x, position_y, self.font_size, color)

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.options)

    def select(self):
        return self.selected_index
