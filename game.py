from pyray import *
from scenes.scene_menu import MenuScene

class Game:
    def __init__(self):
        # Init audio device (safe no-op if already open)
        if not is_audio_device_ready():
            init_audio_device()
        
        # Load all music streams
        self.music_tracks = {
            "normal":   load_music_stream("assets/sounds/music1.wav"),
            "inverted": load_music_stream("assets/sounds/music1Reversed.wav"),
            "battle":   load_music_stream("assets/sounds/battleMusic.mp3"),
        }
        for track in self.music_tracks.values():
            set_music_volume(track, 0.6)
        
        # SFX
        self.fall_sfx = load_sound("assets/sounds/8bitFall.mp3")
        self.win_sfx  = load_sound("assets/sounds/winEffect.mp3")
        
        # Start with normal music
        self.active_track_name = "normal"
        play_music_stream(self.music_tracks["normal"])
        
        # Pending track switch: wait until fall SFX finishes before starting new music
        self._pending_track = None
        
        self.current_scene = MenuScene(self)
        
    def switch_music(self, track_name):
        """Switch to a different music track with a fall SFX transition."""
        if track_name == self.active_track_name and self._pending_track is None:
            return  # Already playing / already switching to this track
        
        # Stop all tracks cleanly
        for track in self.music_tracks.values():
            stop_music_stream(track)
        
        # Play the fall sting
        play_sound(self.fall_sfx)
        
        self.active_track_name = track_name
        self._pending_track = track_name
        
    def play_win_effect(self):
        """Stop music, play the win jingle, then resume normal music."""
        for track in self.music_tracks.values():
            stop_music_stream(track)
        play_sound(self.win_sfx)
        # Queue normal music to start once the win SFX finishes via _pending_win
        self.active_track_name = "normal"
        self._pending_win = True
        self._pending_track = None  # don't use fall transition

    def change_scene(self, scene):
        self.current_scene = scene
        
    def update(self, dt):
        # Handle pending win effect → resume music1 after jingle finishes
        if getattr(self, '_pending_win', False):
            if not is_sound_playing(self.win_sfx):
                play_music_stream(self.music_tracks["normal"])
                self._pending_win = False
            return  # Don't process pending_track while win jingle is playing
        
        # If we have a pending track to start, wait until the fall SFX finishes
        if self._pending_track is not None:
            if not is_sound_playing(self.fall_sfx):
                play_music_stream(self.music_tracks[self._pending_track])
                self._pending_track = None
        
        # Keep active track streaming
        update_music_stream(self.music_tracks[self.active_track_name])
        
        if self.current_scene:
            self.current_scene.update(dt)
            
    def draw(self):
        if self.current_scene:
            self.current_scene.draw()