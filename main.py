from raylibpy import *
from floor import Floor
from player import Player
from ui import PlayerUI
from enum import Enum
import time
import textures
from config import *
from raylibpy import load_sound, play_sound, unload_sound

#Init
init_window(W, H, "My Game")
set_exit_key(0)
init_audio_device()
textures.load_textures()
config = load_config()

# Load background music
music = load_music_stream("assets/audio/rpg-city-8381.mp3")
play_music_stream(music)

#player stuff
player_texture = load_texture("assets/player_sheet/player_spritesheet.png")
player = Player(player_texture)
playerui = PlayerUI(player, music, config)
floor = Floor()

# Game state enum
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3
    SETTINGS = 4

game_state = GameState.MAIN_MENU
previous_state = None #used to track last state (used for settings menu primarily)

def restart_game():
    global game_state, player, floor, playerui
    game_state = GameState.PLAYING
    player = Player(player_texture)
    floor = Floor()
    playerui = PlayerUI(player, music, config)

# Main game loop

while not window_should_close():

    # Update music stream if music is loaded
    if music:
        update_music_stream(music)
    #pause/unpause button
    if is_key_pressed(KEY_ESCAPE):
        if game_state == GameState.PLAYING:
            game_state = GameState.PAUSED
        elif game_state == GameState.PAUSED:
            game_state = GameState.PLAYING
        elif game_state == GameState.SETTINGS:
            game_state = GameState.PAUSED
    # Drawing
    begin_drawing()
    clear_background(SKYBLUE)

    if game_state == GameState.MAIN_MENU:
        action = playerui.draw_main_menu()
        if action == "start":
            game_state = GameState.PLAYING
        elif action == "settings":
            previous_state = game_state #stores current game state
            game_state = GameState.SETTINGS
        elif action == "quit":
            close_window()

        #prevents game from rendering in main menu (until player clicks play)
        end_drawing()
        continue

    # Check for player death and update game state
    if game_state == GameState.PLAYING and player.health <= 0:
        game_over_timer = time.time()
        game_state = GameState.GAME_OVER

    #allows animations in every state but paused and settings
    if game_state != GameState.PAUSED and game_state != GameState.SETTINGS:
        player.update(floor.get_current_room())
        floor.update(player)
        playerui.update()

    floor.draw()
    player.draw()
    playerui.draw(floor)

    if game_state == GameState.PAUSED:
        action = playerui.draw_pause_menu()
        if action == "resume":
            game_state = GameState.PLAYING
        elif action == "settings":
            previous_state = game_state #stores current game state
            game_state = GameState.SETTINGS
            end_drawing()
            continue
        elif action == "quit":
            game_state = GameState.MAIN_MENU

    if game_state == GameState.SETTINGS:
        action = playerui.draw_settings_menu(previous_state)
        if action == "back":
            game_state = previous_state
        end_drawing()
        continue

    # Draw game over overlay if in game over state
    if game_state == GameState.GAME_OVER:
        playerui.draw_game_over(restart_game)

    end_drawing()

# Unload resources
unload_texture(player_texture)
unload_music_stream(music)  # Unload the music stream
close_window()
