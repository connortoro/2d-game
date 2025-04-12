from raylibpy import *

class Menu:
    def __init__(self):
        self.main_options = ["Resume", "Options", "Quit"]
        self.options_menu = ["Music Volume", "Back"]
        self.selected_index = 0
        self.font_size = 40
        self.spacing = 10
        self.active_color = RED
        self.inactive_color = WHITE
        self.state = "main"
        self.music_volume = 0.1

    def draw(self, screen_width, screen_height):
        if not is_window_ready():
            return
        
        options = self.main_options if self.state == "main" else self.options_menu
        
        for i, option in enumerate(options):
            display_text = option
            if self.state == "options" and option == "Music Volume":
                display_text = f"Music Volume: {int(self.music_volume * 100)}%"

            color = self.active_color if i == self.selected_index else self.inactive_color
            text_width = measure_text(display_text, self.font_size)
            position_x = (screen_width - text_width) // 2
            position_y = (screen_height // 2) + i * (self.font_size + self.spacing)

            draw_text(display_text, position_x, position_y, self.font_size, color)

            if self.state == "options" and option == "Music Volume" and i == self.selected_index:
                self.draw_music_volume_bar(screen_width, position_y)

    def navigate(self, direction):
        options = self.main_options if self.state == "main" else self.options_menu
        self.selected_index = (self.selected_index + direction) % len(options)

    def select(self):
        if self.state == "main":
            return self.selected_index
        elif self.state == "options":
            if self.selected_index == 1:  # Back
                self.state = "main"
                self.selected_index = 1  # Focus back on Options
        return None
    
    def adjust_volume(self, direction, music):
        # Change volume in 10% steps
        self.music_volume = min(1.0, max(0.0, self.music_volume + direction * 0.1))
        set_music_volume(music, self.music_volume)

    def draw_music_volume_bar(self, screen_width, position_y):
        bar_width = 200
        bar_height = 20
        bar_x = (screen_width - bar_width) // 2
        bar_y = position_y + self.font_size + 10

        filled_width = int(bar_width * self.music_volume)

        # Draw empty bar
        draw_rectangle(bar_x, bar_y, bar_width, bar_height, GRAY)

        # Draw filled portion
        draw_rectangle(bar_x, bar_y, filled_width, bar_height, GREEN)

        # Draw percentage text
        # percent_text = f"{int(self.music_volume * 100)}%"
        # text_width = measure_text(percent_text, 20)
        # draw_text(percent_text, bar_x + (bar_width - text_width) // 2, bar_y + bar_height + 5, 20, WHITE)