"""
Asset loader for warehouse picker game.
Loads and manages all game sprites and images.
"""

import pygame
import os

class AssetLoader:
    """Loads and stores all game assets."""
    
    def __init__(self):
        self.assets = {}
        self.base_path = "assets"
        self.images_path = os.path.join(self.base_path, "images")
        self.audio_path = os.path.join(self.base_path, "audio")
        
        # Create assets directories if they don't exist
        self._create_directories()
        
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.base_path,
            self.images_path,
            self.audio_path,
            os.path.join(self.base_path, "floor"),
            os.path.join(self.base_path, "walls"),
            os.path.join(self.base_path, "delivery"),
            os.path.join(self.base_path, "shelves"),
            os.path.join(self.base_path, "products"),
            os.path.join(self.base_path, "pickers")
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"📁 Created directory: {directory}")
        
        print("⚠️ Please add your asset files to the appropriate folders.")
    
    def load_all(self):
        """Load all game assets."""
        print("📦 Loading game assets...")
        
        # Try to load real assets, create placeholders for missing ones
        self._load_menu_images()
        self._load_audio()
        self._load_or_create_floor()
        self._load_or_create_walls()
        self._load_or_create_delivery()
        self._load_or_create_shelves()
        self._load_or_create_products()
        self._load_or_create_pickers()
        
        print("✅ All assets loaded successfully!")
        return self.assets
    
    def _load_menu_images(self):
        """Load menu and UI images."""
        # Title background
        title_bg_path = os.path.join(self.images_path, "title_background.png")
        image = self._load_image_safe(title_bg_path)
        
        if image:
            self.assets["title_background"] = image
            print("   ✓ Title background loaded")
        else:
            # Create placeholder title background
            surf = pygame.Surface((1200, 800))
            # Gradient background
            for i in range(800):
                color_value = int(20 + (i / 800) * 40)
                pygame.draw.line(surf, (color_value, color_value, 80), (0, i), (1200, i))
            # Add title text
            font = pygame.font.Font(None, 100)
            title_text = font.render("WAREHOUSE PICKER", True, (255, 255, 100))
            title_rect = title_text.get_rect(center=(600, 200))
            surf.blit(title_text, title_rect)
            
            font = pygame.font.Font(None, 36)
            subtitle = font.render("Press any key or click to continue", True, (255, 255, 255))
            subtitle_rect = subtitle.get_rect(center=(600, 700))
            surf.blit(subtitle, subtitle_rect)
            
            self.assets["title_background"] = surf
            print("   ⚠️ Title background: Using placeholder")
        
        # Button images (if they exist)
        button_images = ["button_normal", "button_hover", "button_pressed"]
        for button in button_images:
            button_path = os.path.join(self.images_path, f"{button}.png")
            image = self._load_image_safe(button_path)
            
            if image:
                self.assets[button] = image
            else:
                # We'll create buttons dynamically in menu.py
                pass
        print("   ✓ Menu images loaded/created")
    
    def _load_audio(self):
        """Load audio files."""
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Audio files - support both .mp3 and .wav
        audio_files = {
            "background_music": ["background_music.mp3", "background_music.wav"],
            "button_click": ["button_click.mp3", "button_click.wav"],
            "ui_click": ["ui_click.mp3", "ui_click.wav"],
            "pickup_sound": ["pickup_sound.mp3", "pickup_sound.wav"],
            "deliver_sound": ["deliver_sound.mp3", "deliver_sound.wav"]
        }
        
        for key, filenames in audio_files.items():
            sound_loaded = False
            
            for filename in filenames:
                audio_path = os.path.join(self.audio_path, filename)
                
                if os.path.exists(audio_path):
                    try:
                        if key == "background_music":
                            # Music is loaded differently
                            self.assets[key] = audio_path
                            print(f"   ✓ {key} loaded ({filename})")
                        else:
                            # Sound effects
                            if filename.endswith('.mp3'):
                                # For MP3 files, we need to use a different approach
                                # Pygame's Sound doesn't support MP3 well, so we convert
                                import tempfile
                                import subprocess
                                
                                # Try to load using pygame.mixer.Sound (might not work for MP3)
                                try:
                                    sound = pygame.mixer.Sound(audio_path)
                                    self.assets[key] = sound
                                    print(f"   ✓ {key} loaded ({filename})")
                                except:
                                    # If MP3 loading fails, create a silent placeholder
                                    print(f"   ⚠️ {filename} is MP3 format which may not work well with Pygame")
                                    print(f"   ⚠️ Consider converting to WAV format for better compatibility")
                                    self.assets[key] = pygame.mixer.Sound(buffer=bytes([0] * 44))
                            else:
                                # WAV files load normally
                                sound = pygame.mixer.Sound(audio_path)
                                self.assets[key] = sound
                                print(f"   ✓ {key} loaded ({filename})")
                        
                        sound_loaded = True
                        break
                        
                    except Exception as e:
                        print(f"   ✗ Error loading {filename}: {e}")
            
            if not sound_loaded:
                print(f"   ⚠️ No audio file found for {key}, using silent placeholder")
                if key != "background_music":
                    self.assets[key] = pygame.mixer.Sound(buffer=bytes([0] * 44))
                else:
                    self.assets[key] = None
        
        print("   ✓ Audio files loaded")
    
    def _load_image_safe(self, path):
        """Safely load an image, handling display initialization issues."""
        try:
            if os.path.exists(path):
                # Try to load normally
                image = pygame.image.load(path)
                # Try to convert, but if display isn't initialized, skip conversion
                try:
                    return image.convert_alpha()
                except:
                    return image
            return None
        except Exception as e:
            print(f"   Warning: Could not load {path}: {e}")
            return None
    
    def _load_or_create_floor(self):
        """Load floor tile or create placeholder."""
        floor_path = os.path.join(self.base_path, "floor", "floor.png")
        image = self._load_image_safe(floor_path)
        
        if image:
            self.assets["floor"] = image
            print("   ✓ Floor tile loaded")
        else:
            # Create placeholder
            surf = pygame.Surface((64, 64))
            surf.fill((100, 100, 100))  # Gray
            # Add grid pattern
            for i in range(0, 64, 16):
                pygame.draw.line(surf, (80, 80, 80), (i, 0), (i, 64), 1)
                pygame.draw.line(surf, (80, 80, 80), (0, i), (64, i), 1)
            self.assets["floor"] = surf
            print("   ⚠️ Floor tile: Using placeholder")
    
    def _load_or_create_walls(self):
        """Load wall tiles or create placeholders."""
        walls = ["left", "right", "corner"]
        for wall in walls:
            wall_path = os.path.join(self.base_path, "walls", f"wall_{wall}.png")
            image = self._load_image_safe(wall_path)
            
            if image:
                self.assets[f"wall_{wall}"] = image
            else:
                # Create placeholder
                surf = pygame.Surface((64, 64))
                if wall == "corner":
                    surf.fill((120, 120, 120))
                else:
                    surf.fill((110, 110, 110))
                # Add brick pattern
                for i in range(0, 64, 16):
                    for j in range(0, 64, 32):
                        offset = 8 if i % 32 == 0 else 0
                        pygame.draw.rect(surf, (100, 100, 100), 
                                       (i, j + offset, 16, 16), 1)
                self.assets[f"wall_{wall}"] = surf
        print("   ✓ Wall tiles loaded/created")
    
    def _load_or_create_delivery(self):
        """Load delivery zone or create placeholder."""
        delivery_path = os.path.join(self.base_path, "delivery", "delivery_zone.png")
        image = self._load_image_safe(delivery_path)
        
        if image:
            self.assets["delivery"] = image
            print("   ✓ Delivery zone loaded")
        else:
            # Create placeholder
            surf = pygame.Surface((64, 64))
            surf.fill((50, 150, 50))  # Green
            # Add arrows
            pygame.draw.polygon(surf, (255, 255, 255), 
                              [(32, 15), (25, 35), (39, 35)])
            pygame.draw.polygon(surf, (255, 255, 255), 
                              [(32, 49), (25, 29), (39, 29)])
            self.assets["delivery"] = surf
            print("   ⚠️ Delivery zone: Using placeholder")
    
    def _load_or_create_shelves(self):
        """Load shelf sprites or create placeholders."""
        shelf_types = [
            "bread", "eggs", "milk", "chocolate", 
            "apples", "toilet_paper", "chips"
        ]
        
        for shelf_type in shelf_types:
            shelf_path = os.path.join(self.base_path, "shelves", f"{shelf_type}_shelf.png")
            image = self._load_image_safe(shelf_path)
            
            if image:
                self.assets[f"shelf_{shelf_type}"] = image
            else:
                # Create placeholder
                surf = pygame.Surface((64, 64))
                # Brown wood color for shelves
                surf.fill((139, 69, 19))
                # Add shelf details
                pygame.draw.rect(surf, (160, 82, 45), (0, 0, 64, 8))  # Top shelf
                pygame.draw.rect(surf, (160, 82, 45), (0, 56, 64, 8))  # Bottom shelf
                for i in range(0, 64, 16):
                    pygame.draw.rect(surf, (120, 60, 20), (i, 0, 2, 64))  # Vertical dividers
                self.assets[f"shelf_{shelf_type}"] = surf
        
        print("   ✓ Shelf sprites loaded/created")
    
    def _load_or_create_products(self):
        """Load product sprites or create placeholders."""
        product_types = [
            "bread", "eggs", "milk", "chocolate",
            "apples", "toilet_paper", "chips"
        ]
        
        for product in product_types:
            product_path = os.path.join(self.base_path, "products", f"{product}_item.png")
            image = self._load_image_safe(product_path)
            
            if image:
                self.assets[f"item_{product}"] = image
            else:
                # Create placeholder (already sized at 40x40 from previous changes)
                surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                # Different colors for different products
                colors = {
                    "bread": (210, 180, 140),
                    "eggs": (255, 255, 240),
                    "milk": (240, 240, 255),
                    "chocolate": (101, 67, 33),
                    "apples": (255, 50, 50),
                    "toilet_paper": (255, 255, 230),
                    "chips": (255, 200, 50)
                }
                color = colors.get(product, (200, 200, 200))
                
                # Simple shapes for each product
                if product == "bread":
                    pygame.draw.ellipse(surf, color, (6, 10, 28, 20))
                elif product == "eggs":
                    pygame.draw.ellipse(surf, color, (10, 5, 20, 30))
                elif product == "milk":
                    pygame.draw.rect(surf, color, (8, 5, 24, 30))
                elif product == "chocolate":
                    pygame.draw.rect(surf, color, (5, 12, 30, 18))
                elif product == "apples":
                    pygame.draw.circle(surf, color, (20, 20), 14)
                elif product == "toilet_paper":
                    pygame.draw.circle(surf, color, (20, 20), 16)
                elif product == "chips":
                    pygame.draw.ellipse(surf, color, (5, 12, 30, 18))
                
                self.assets[f"item_{product}"] = surf
        
        print("   ✓ Product sprites loaded/created")
    
    def _load_or_create_pickers(self):
        """Load picker sprites or create placeholders."""
        # Player picker
        player_path = os.path.join(self.base_path, "pickers", "player.png")
        image = self._load_image_safe(player_path)
        
        if image:
            self.assets["player"] = image
        else:
            # Create placeholder player
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Green body
            pygame.draw.rect(surf, (50, 200, 50), (4, 4, 24, 24))
            pygame.draw.rect(surf, (30, 180, 30), (4, 4, 24, 24), 2)
            # Face/eyes
            pygame.draw.circle(surf, (255, 255, 255), (12, 12), 4)
            pygame.draw.circle(surf, (255, 255, 255), (20, 12), 4)
            self.assets["player"] = surf
        
        # AI picker
        ai_path = os.path.join(self.base_path, "pickers", "ai.png")
        image = self._load_image_safe(ai_path)
        
        if image:
            self.assets["ai"] = image
        else:
            # Create placeholder AI
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Red body
            pygame.draw.rect(surf, (200, 50, 50), (4, 4, 24, 24))
            pygame.draw.rect(surf, (180, 30, 30), (4, 4, 24, 24), 2)
            # Robot face
            pygame.draw.rect(surf, (255, 255, 255), (8, 8, 16, 8))
            pygame.draw.rect(surf, (100, 100, 100), (10, 10, 4, 4))
            pygame.draw.rect(surf, (100, 100, 100), (18, 10, 4, 4))
            self.assets["ai"] = surf
        
        print("   ✓ Picker sprites loaded/created")
    
    def get_asset(self, name):
        """Get an asset by name."""
        return self.assets.get(name)
    
    def scale_asset(self, name, new_size):
        """Scale an asset to new size."""
        if name in self.assets and self.assets[name] is not None and isinstance(self.assets[name], pygame.Surface):
            original = self.assets[name]
            self.assets[name] = pygame.transform.scale(original, new_size)