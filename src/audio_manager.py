"""
Audio manager for the warehouse picker game.
Handles background music and sound effects.
"""

import pygame
import json
import os

class AudioManager:
    """Manages all audio in the game."""
    
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.7  # Default volume (0.0 to 1.0)
        self.sfx_volume = 0.8    # Default volume (0.0 to 1.0)
        self.is_music_enabled = True
        self.is_sfx_enabled = True
        self.settings_file = "game_settings.json"
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Load settings if they exist
        self.load_settings()
    
    def load_sounds(self, asset_loader):
        """Load all sound effects from the asset loader."""
        # Background music
        self.background_music = asset_loader.get_asset("background_music")
        
        # Sound effects
        sound_names = ["button_click", "ui_click", "pickup_sound", "deliver_sound"]
        for name in sound_names:
            sound = asset_loader.get_asset(name)
            if sound:
                self.sounds[name] = sound
                print(f"   ✓ Loaded sound: {name}")
            else:
                print(f"   ⚠️ Sound not found: {name}")
    
    def play_background_music(self):
        """Start playing background music."""
        if self.is_music_enabled and self.background_music:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                print("   ✓ Background music started")
            except Exception as e:
                print(f"   ✗ Error playing background music: {e}")
    
    def stop_background_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
    
    def play_sound(self, sound_name):
        """Play a sound effect."""
        if self.is_sfx_enabled and sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(self.sfx_volume)
                sound.play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_music(self):
        """Toggle music on/off."""
        self.is_music_enabled = not self.is_music_enabled
        if self.is_music_enabled:
            self.play_background_music()
        else:
            self.stop_background_music()
        return self.is_music_enabled
    
    def toggle_sfx(self):
        """Toggle SFX on/off."""
        self.is_sfx_enabled = not self.is_sfx_enabled
        return self.is_sfx_enabled
    
    def save_settings(self):
        """Save audio settings to file."""
        settings = {
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "is_music_enabled": self.is_music_enabled,
            "is_sfx_enabled": self.is_sfx_enabled
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print("✓ Audio settings saved")
        except Exception as e:
            print(f"✗ Error saving audio settings: {e}")
    
    def load_settings(self):
        """Load audio settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                self.music_volume = settings.get("music_volume", self.music_volume)
                self.sfx_volume = settings.get("sfx_volume", self.sfx_volume)
                self.is_music_enabled = settings.get("is_music_enabled", self.is_music_enabled)
                self.is_sfx_enabled = settings.get("is_sfx_enabled", self.is_sfx_enabled)
                
                print("✓ Audio settings loaded")
        except Exception as e:
            print(f"✗ Error loading audio settings: {e}")