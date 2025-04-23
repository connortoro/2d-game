from raylibpy import *

class SoundManager:
    def __init__(self, config):
        self.config = config
        self.game_volume = self.config.get("game_volume", 1.0)
        self.sounds = {}

        self.music_tracks = {}
        self.current_music = None
        self.music_volume = self.config.get("music_volume", 1.0)

        self.load_sounds()
        self.load_music()

    def load_sounds(self):
        self.sounds["attack"] = load_sound("assets/audio/sword-sound-260274.wav")
        self.sounds["footstep_sound"] = load_sound("assets/audio/08_Step_rock_02.wav")
        self.sounds["hit_sound"] = load_sound("assets/audio/Sword Impact Hit 2.wav")
        self.sounds["coin"] = load_sound("assets/audio/retro-coin-1-236677.mp3")
        self.sounds["heart"] = load_sound("assets/audio/bubble-pop-2-293341.wav")
        self.set_all_sounds_volume(self.game_volume)

        set_sound_pitch(self.sounds["hit_sound"], 0.8)
        set_sound_pitch(self.sounds["coin"], 0.8)
    def load_music(self):
        self.music_tracks["level_1_music"] = load_music_stream("assets/audio/rpg-city-8381.mp3")
        self.music_tracks["main_menu_music"] = load_music_stream("assets/audio/main_menu_music.mp3")
        set_music_volume(self.music_tracks["level_1_music"], self.music_volume)
        set_music_volume(self.music_tracks["main_menu_music"], self.music_volume)

    def set_all_sounds_volume(self, volume):
        for sound in self.sounds.values():
            set_sound_volume(sound, volume)

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            play_sound(self.sounds[sound_name])
        return
    
    def play_music(self, music_name):
        if music_name in self.music_tracks:
            if self.current_music and is_music_stream_playing(self.current_music):
                stop_music_stream(self.current_music)

            self.current_music = self.music_tracks[music_name]
            play_music_stream(self.current_music)
            set_music_volume(self.current_music, self.music_volume)
    
    def update_game_volume(self, new_volume):
        self.game_volume = new_volume
        self.set_all_sounds_volume(self.game_volume)

    def update_music_volume(self, new_volume):
        self.music_volume = new_volume
        if self.current_music:
            set_music_volume(self.current_music, self.music_volume)