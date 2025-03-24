from raylibpy import *
from floor import Floor
from player import Player, W, H
from ui import PlayerUI
from npc import NPC
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
    score_text = f"Total score: {player.get_score()}"
    game_over_text_width = measure_text(game_over_text, 60)
    score_text_width = measure_text(score_text, 40)
    draw_text(game_over_text, W/2 - game_over_text_width/2, H/2 - 100, 60, RED)
    draw_text(score_text, W/2 - score_text_width/2, H/2 - 50, 40, WHITE)  # Centered properly
    
    
    #draw buttons (only after delay)
    if time.time() - game_over_timer > game_over_delay:
        #restart button
        draw_rectangle_rec(restart_button, DARKGRAY)
        restart_text = "Restart"
        restart_width = measure_text(restart_text, 30)
        draw_text(restart_text, restart_button.x + (restart_button.width/2) - restart_width/2, 
                 restart_button.y + 10, 30, WHITE)
        

# Main game loop
insufficient_score = False

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
    #instructions to display
    instructions_text = [
    "Controls:",
    "W, A, S, D: Move",
    "Arrow Up, Down, Left, Right: Attack Direction",
    "E: Interact",
    "X: Exit Dialog",
    "Kill as many enemies as you can before dying!"
    ]
    # Drawing
    begin_drawing()
    
    
    # Always draw the game
    clear_background(SKYBLUE)
    floor.draw()
    player.draw()
    playerui.draw(floor)

    #instruction box
    instructions_background_height = 140
    draw_rectangle(20, H - instructions_background_height - 10, 500, instructions_background_height, Color(0, 0, 0, 180))
    #draws instructions
    for i, line in enumerate(instructions_text):
        draw_text(line, 25, H - 140 + (i * 20), 20, WHITE)
    if player.in_dialog:
        if insufficient_score:
            draw_text("Not enough score!", W/2 - measure_text("Not enough score!", 40)/2, H/2, 40, RED)
            draw_text("Press ENTER to continue.", W/2 - measure_text("Press ENTER to continue.", 20)/2, H/2 + 50, 20, WHITE)
            if is_key_pressed(KEY_ENTER):
                insufficient_score = False  
        else:
            draw_rectangle(100, 400, 600, 150, DARKGRAY)
            draw_text("Hello, hero! Choose an upgrade:              ('x' to exit)", 110, 410, 20, WHITE)
            draw_text("1: Increase Health (30 Score)", 110, 440, 20, WHITE)
            draw_text("2: Increase Speed (20 Score)", 110, 470, 20, WHITE)
            draw_text("3: Increase Attack (40 Score)", 110, 500, 20, WHITE)


            if is_key_pressed(KEY_ONE):
                if player.score < 30:  
                    insufficient_score = True
                else:
                    player.increase_health(10)
                    player.score -= 30
                    player.in_dialog = False
            elif is_key_pressed(KEY_TWO):
                if player.score < 20:  
                    insufficient_score = True
                else:
                    player.increase_speed(2)
                    player.score -= 20
                    player.in_dialog = False
            elif is_key_pressed(KEY_THREE):
                if player.score < 40: 
                    insufficient_score = True
                else:
                    player.increase_attack(5)
                    player.score -= 40
                    player.in_dialog = False
            elif is_key_pressed(KEY_X):
                player.in_dialog = False
    
    # Draw game over overlay if in game over state
    if game_state == GameState.GAME_OVER:
        draw_game_over()
    
    end_drawing()

playerui.unload()
unload_texture(player_texture)
close_window()