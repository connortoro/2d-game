from raylibpy import *
from floor import Floor
from player import Player
from ui import PlayerUI
from enum import Enum
import time
import textures
from config import *
from raylibpy import load_sound, play_sound, unload_sound
from menu import Menu

#Init
init_window(W, H, "My Game")
set_exit_key(0)
init_audio_device()
textures.load_textures()

# init_audio_device()
player_texture = load_texture("assets/player_sheet/player_spritesheet.png")
player = Player(player_texture)
playerui = PlayerUI(player)
floor = Floor()
menu = Menu()

# Load background music
music = load_music_stream("assets/audio/rpg-city-8381.mp3")
play_music_stream(music)
set_music_volume(music, 0.1)

# Game state enum
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    PAUSED = 2

game_state = GameState.PLAYING #base game_state

def restart_game():
    global game_state, player, floor, playerui
    game_state = GameState.PLAYING
    player = Player(player_texture)
    floor = Floor()
    playerui = PlayerUI(player)

def handle_pause():
    global game_state, menu

    if game_state == GameState.PLAYING and is_key_pressed(KEY_ESCAPE):
        game_state = GameState.PAUSED  # Enter Pause Mode
    elif game_state == GameState.PAUSED:
        if menu.state == "main":
            if is_key_pressed(KEY_ESCAPE):
                game_state = GameState.PLAYING

        if is_key_pressed(KEY_DOWN):
            menu.navigate(1)
        elif is_key_pressed(KEY_UP):
            menu.navigate(-1)
        elif is_key_pressed(KEY_ENTER):
            selection = menu.select()
            if selection == 0:  # Resume
                game_state = GameState.PLAYING
            elif selection == 1:
                menu.state = "options"
                menu.selected_index = 0
            elif selection == 2:  # Quit
                close_window()  # Close window only if Quit is selected from menu
                exit()

        elif menu.state == "options":
            if is_key_pressed(KEY_RIGHT):
                if menu.selected_index == 0:
                    menu.adjust_volume(1, music)
            elif is_key_pressed(KEY_LEFT):
                if menu.selected_index == 0:
                    menu.adjust_volume(-1, music)
            elif is_key_pressed(KEY_DOWN):
                menu.navigate(1)
            elif is_key_pressed(KEY_UP):
                menu.navigate(-1)
            elif is_key_pressed(KEY_ENTER):
                menu.select()



# Main game loop

while not window_should_close():
    # Update music stream if music is loaded
    if music:
        update_music_stream(music)

    # Drawing
    begin_drawing()
    clear_background(SKYBLUE)

    # Check for player death and update game state
    if game_state == GameState.PLAYING and player.health <= 0:
        game_over_timer = time.time()
        game_state = GameState.GAME_OVER

    #allows animations in every state but paused
    if game_state != GameState.PAUSED:
        player.update(floor.get_current_room())
        floor.update(player)
        playerui.update()

    floor.draw()
    player.draw()
    playerui.draw(floor)

    handle_pause()

    if game_state == GameState.PAUSED:
        menu.draw(W, H)

    # Draw game over overlay if in game over state
    if game_state == GameState.GAME_OVER:
        playerui.draw_game_over(restart_game)

    end_drawing()

# Unload resources
unload_texture(player_texture)
unload_music_stream(music)  # Unload the music stream
close_window()
