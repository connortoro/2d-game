from raylibpy import *
from room import Room
from floor import Floor
from player import Player, W, H
from ui import PlayerUI
from enum import Enum
import time

#Init
init_window(W, H, "My Game")
player_texture = load_texture("assets/player_sheet/player.png")
player = Player(player_texture)
playerui = PlayerUI(player)
floor = Floor()


# Game state enum
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    PAUSED = 2


game_state = GameState.PLAYING
game_over_timer = 0
game_over_delay = 2.0  #seconds to wait after death before showing game over screen
restart_button = Rectangle(W/2 - 100, H/2 + 100, 200, 50)
main_menu_button = Rectangle(W/2 - 100, H/2 + 160, 200, 50)


def restart_game():
    global game_state, player, floor, playerui
    
    # Reset game state
    game_state = GameState.PLAYING
    
    # Reset player
    player = Player(player_texture)
    
    # Reset floor/rooms
    floor = Floor()
    
    # Reset health bar and inventory
    playerui = PlayerUI(player)

def draw_game_over():
    #draw semi-transparent backgorund
    draw_rectangle(0, 0, W, H, Color(0, 0, 0, 200))
    
    #draw game over text
    game_over_text = "GAME OVER"
    text_width = measure_text(game_over_text, 60)
    draw_text(game_over_text, W/2 - text_width/2, H/2 - 100, 60, RED)
    
    
    #draw buttons (only after delay)
    if time.time() - game_over_timer > game_over_delay:
        #restart button
        draw_rectangle_rec(restart_button, DARKGRAY)
        restart_text = "Restart"
        restart_width = measure_text(restart_text, 30)
        draw_text(restart_text, restart_button.x + (restart_button.width/2) - restart_width/2, 
                 restart_button.y + 10, 30, WHITE)
        

# Main game loop
while not window_should_close():
    # Check for player death and update game state
    if game_state == GameState.PLAYING and player.health <= 0:
        game_over_timer = time.time()
        game_state = GameState.GAME_OVER
    
    # Always update everything, regardless of game state
    player.update(floor.get_current_room())
    floor.update(player)
    playerui.update()
    
    # Game over state button logic
    if game_state == GameState.GAME_OVER:
        if time.time() - game_over_timer > game_over_delay:
            if is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
                mouse_pos = get_mouse_position()
                if check_collision_point_rec(mouse_pos, restart_button):
                    restart_game()
    
    # Drawing
    begin_drawing()
    
    # Always draw the game
    clear_background(SKYBLUE)
    floor.draw()
    player.draw()
    playerui.draw_health_bar()
    playerui.draw_inventory_bar()
    
    # Draw game over overlay if in game over state
    if game_state == GameState.GAME_OVER:
        draw_game_over()
    
    end_drawing()

playerui.unload()
unload_texture(player_texture)
close_window()