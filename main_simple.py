"""
Warehouse Picker Game - Main File
Main entry point for the game
"""

import pygame
import sys
import random
import time
import traceback
from src.asset_loader import AssetLoader
from src.warehouse import Warehouse, CellType, ProductType
from src.player import Player
from src.ai_picker import AIPicker

# Initialize Pygame
pygame.init()

# Screen configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

class Game:
    def __init__(self):
        print("Initializing game...")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Warehouse Picker")
        self.clock = pygame.time.Clock()
        self.running = True
        
        try:
            print("Loading assets...")
            self.asset_loader = AssetLoader()
            self.asset_loader.load_all()
            
            # Game state
            self.level = 1
            self.score = 0
            self.orders = []
            
            # Timer system
            self.level_time = 120.0
            self.time_remaining = self.level_time
            
            # Game state
            self.game_state = "playing"
            
            print("Setting up level...")
            self._setup_level()
            
            print("Game initialized successfully!")
            
        except Exception as e:
            print(f"ERROR during initialization: {e}")
            traceback.print_exc()
            self._show_error_screen(f"Initialization Error: {str(e)}")
    
    def _setup_level(self):
        """Set up a new level."""
        print(f"Setting up level {self.level}...")
        
        # Reset timer
        self.time_remaining = self.level_time
        
        # Generate simple order
        self._generate_simple_order()
        
        # Create a simple warehouse without complex placement
        print("Creating simple warehouse...")
        self._create_simple_warehouse()
        
        print("Creating player...")
        self.player = Player(100, 100, self.asset_loader)
        
        print("Level setup complete!")
    
    def _generate_simple_order(self):
        """Generate a simple order."""
        self.orders = [
            {'product': ProductType.BREAD, 'quantity': 1, 'collected': 0},
            {'product': ProductType.EGGS, 'quantity': 1, 'collected': 0}
        ]
        print(f"Order: Bread x1, Eggs x1")
    
    def _create_simple_warehouse(self):
        """Create a simple warehouse for testing."""
        try:
            # Create a simple 10x10 warehouse
            self.warehouse = Warehouse(
                x_offset=50,
                y_offset=100,
                width=10,
                height=10,
                cell_size=64,
                asset_loader=self.asset_loader,
                level=self.level,
                required_products=[ProductType.BREAD, ProductType.EGGS]
            )
            print("Warehouse created successfully")
        except Exception as e:
            print(f"ERROR creating warehouse: {e}")
            traceback.print_exc()
            # Create a fallback warehouse
            self._create_fallback_warehouse()
    
    def _create_fallback_warehouse(self):
        """Create a fallback warehouse if the main one fails."""
        print("Creating fallback warehouse...")
        
        # Create a very simple manual warehouse
        from src.warehouse import CellType, ProductType
        
        self.warehouse = type('SimpleWarehouse', (), {})()
        self.warehouse.width = 10
        self.warehouse.height = 10
        self.warehouse.cell_size = 64
        self.warehouse.x_offset = 50
        self.warehouse.y_offset = 100
        self.warehouse.shelf_products = {
            (2, 2): {'type': ProductType.BREAD, 'quantity': 5},
            (5, 5): {'type': ProductType.EGGS, 'quantity': 5}
        }
        self.warehouse.delivery_zones = [(7, 7)]
        
        # Simple methods
        self.warehouse.get_cell_at_pixel = lambda x, y: (int((x-50)/64), int((y-100)/64))
        self.warehouse.get_pixel_position = lambda x, y: (50 + x*64 + 32, 100 + y*64 + 32)
        self.warehouse.get_cell_type = lambda x, y: CellType.SHELF if (x, y) in [(2,2), (5,5)] else CellType.DELIVERY if (x, y) == (7,7) else CellType.AISLE
        self.warehouse.take_product = lambda x, y: self.warehouse.shelf_products[(x, y)]['type'] if (x, y) in self.warehouse.shelf_products else None
        self.warehouse.get_random_walkable_position = lambda: (150, 150)
        
        def draw(screen):
            # Draw a simple grid
            for x in range(10):
                for y in range(10):
                    rect = pygame.Rect(50 + x*64, 100 + y*64, 64, 64)
                    pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            
            # Draw shelves
            for (x, y), info in self.warehouse.shelf_products.items():
                rect = pygame.Rect(50 + x*64, 100 + y*64, 64, 64)
                pygame.draw.rect(screen, (150, 100, 50), rect)
                font = pygame.font.Font(None, 24)
                text = font.render(info['type'].value[:3], True, (255, 255, 255))
                screen.blit(text, (50 + x*64 + 20, 100 + y*64 + 20))
            
            # Draw delivery zone
            x, y = 7, 7
            rect = pygame.Rect(50 + x*64, 100 + y*64, 64, 64)
            pygame.draw.rect(screen, (50, 150, 50), rect)
            font = pygame.font.Font(None, 24)
            text = font.render("DEL", True, (255, 255, 255))
            screen.blit(text, (50 + x*64 + 20, 100 + y*64 + 20))
        
        self.warehouse.draw = draw
        
        print("Fallback warehouse created")
    
    def _show_error_screen(self, error_message):
        """Show error screen."""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            
            self.screen.fill((40, 40, 60))
            
            # Draw error message
            error_text = font.render("ERROR", True, (255, 50, 50))
            self.screen.blit(error_text, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 100))
            
            message_text = small_font.render(error_message, True, (255, 255, 255))
            self.screen.blit(message_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 30))
            
            instruction_text = small_font.render("Press ESC to exit", True, (255, 255, 200))
            self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 30))
            
            pygame.display.flip()
            self.clock.tick(FPS)
    
    def handle_events(self):
        """Handle events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self, delta_time):
        """Update game logic."""
        pass
    
    def draw(self):
        """Draw everything."""
        self.screen.fill((40, 40, 60))
        
        # Draw warehouse
        self.warehouse.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (20, 20))
        
        time_text = font.render(f"Time: {int(self.time_remaining)}s", True, (255, 255, 255))
        self.screen.blit(time_text, (SCREEN_WIDTH - 200, 20))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        last_time = pygame.time.get_ticks()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time
            
            self.handle_events()
            
            if self.game_state == "playing":
                self.time_remaining -= delta_time
                if self.time_remaining <= 0:
                    self.time_remaining = 0
                    self.game_state = "game_over"
            
            self.update(delta_time)
            self.draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)