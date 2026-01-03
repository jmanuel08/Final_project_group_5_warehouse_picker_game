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
from src.audio_manager import AudioManager
from src.menu import Menu

# Initialize Pygame
pygame.init()

# Screen configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BACKGROUND = (40, 40, 60)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT = (255, 255, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        print("Pygame initialized")
        print("Starting game...")
        
        # Create screen (start in windowed mode)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Warehouse Picker")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.game_state = "menu"  # menu, playing, paused, game_over, level_complete
        self.fullscreen = False
        
        try:
            # Load assets
            print("Loading assets...")
            self.asset_loader = AssetLoader()
            self.asset_loader.load_all()
            print("Assets loaded")
            
            # Initialize audio manager
            self.audio_manager = AudioManager()
            self.audio_manager.load_sounds(self.asset_loader)
            self.audio_manager.play_background_music()
            
            # Create menu system
            self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, self.asset_loader, self.audio_manager)
            
            # Game level variables (initialized when game starts)
            self.level = 1
            self.score = 0
            self.orders = []
            self.warehouse = None
            self.player = None
            self.ai_pickers = []
            
            # Timer system - 2 minutes per level
            self.level_time = 120.0  # 2 minutes in seconds
            self.time_remaining = self.level_time
            self.level_start_time = time.time()
            
            # Message system
            self.message = ""
            self.message_timer = 0
            
            # Fonts
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
            self.big_font = pygame.font.Font(None, 48)
            
            print(f"   ✓ Game initialized")
            
        except Exception as e:
            print(f"   ✗ Error during game initialization: {e}")
            traceback.print_exc()
            self._show_error_screen(str(e))
    
    def _show_error_screen(self, error_message):
        """Show an error screen when initialization fails."""
        self.screen.fill(BACKGROUND)
        
        error_text = self.big_font.render("ERROR", True, RED)
        self.screen.blit(error_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 100))
        
        message_text = self.font.render(f"Error: {error_message}", True, TEXT_COLOR)
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 30))
        
        instruction_text = self.small_font.render("Check console for details. Press ESC to exit.", True, HIGHLIGHT)
        self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 30))
        
        pygame.display.flip()
        
        # Wait for ESC key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def _setup_level(self):
        """Set up a new level."""
        print(f"Setting up level {self.level}...")
        
        # Reset timer
        self.time_remaining = self.level_time
        self.level_start_time = time.time()
        
        # Generate order
        self._generate_order()
        
        # Extract unique required products
        required_products = list(set([order['product'] for order in self.orders]))
        print(f"   Required products for level: {[p.value for p in required_products]}")
        
        # Create warehouse with required products
        warehouse_x = 50
        warehouse_y = 100
        warehouse_width = 15
        warehouse_height = 10
        
        print("   Creating warehouse...")
        self.warehouse = Warehouse(
            x_offset=warehouse_x,
            y_offset=warehouse_y,
            width=warehouse_width,
            height=warehouse_height,
            cell_size=64,
            asset_loader=self.asset_loader,
            level=self.level,
            required_products=required_products
        )
        print("   Warehouse created successfully")
        
        # Verify all required products are available
        for product in required_products:
            if not self.warehouse.has_product_available(product):
                print(f"   ⚠️ Warning: Product {product.value} not available in warehouse")
        
        # Create player at walkable position
        print("   Creating player...")
        player_pixel_x, player_pixel_y = self.warehouse.get_random_walkable_position()
        self.player = Player(player_pixel_x, player_pixel_y, self.asset_loader)
        print(f"   Player created at ({player_pixel_x}, {player_pixel_y})")
        
        # Create AI pickers at walkable position - ONLY 1 AI PER LEVEL
        print("   Creating AI pickers...")
        self.ai_pickers = []
        self._reset_ai_pickers()
        print(f"   {len(self.ai_pickers)} AI pickers created")
        
        # Reset message
        self.message = ""
        self.message_timer = 0
        
        print(f"   ✓ Level {self.level} ready. Time starts now!")
    
    def _generate_order(self):
        """Generate a random order with unique products, each with a quantity."""
        self.orders = []
        num_items = min(3 + self.level // 2, 7)
        products = list(ProductType)
        
        # Shuffle and pick unique products
        random.shuffle(products)
        selected_products = products[:num_items]
        
        for product in selected_products:
            quantity = random.randint(1, 3)  # Set how many you need to pick from that shelf
            self.orders.append({
                'product': product,
                'quantity': quantity,
                'collected': 0
            })
        
        print(f"   ✓ Order generated with {num_items} unique products and quantities")

    
    def _reset_ai_pickers(self):
        """Reset AI pickers for the new level - ONLY 1 AI PER LEVEL."""
        self.ai_pickers.clear()
        
        # Create ONE AI with difficulty adjusted to level
        difficulty = min(self.level, 4)  # Maximum difficulty level 4
        
        # ALWAYS create only 1 AI, regardless of level
        num_ai = 1  # Changed from min(1 + self.level // 2, 3) to always 1
        
        for i in range(num_ai):
            # Get a walkable position for AI
            ai_pixel_x, ai_pixel_y = self.warehouse.get_random_walkable_position()
            
            # Slightly adjust position to avoid overlapping
            ai_pixel_x += random.randint(-20, 20)
            ai_pixel_y += random.randint(-20, 20)
            
            ai = AIPicker(ai_pixel_x, ai_pixel_y, self.warehouse, 
                         self.asset_loader, difficulty_level=difficulty)
            ai.assign_order(self.orders.copy())
            self.ai_pickers.append(ai)
        
        print(f"   ✓ {num_ai} AI(s) created with difficulty {difficulty}")
    
    def handle_events(self):
        """Handle game events."""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                        self.menu.current_state = "main_menu"
                    elif self.game_state == "menu":
                        if self.menu.current_state == "main_menu":
                            self.running = False
                        elif self.menu.current_state == "settings":
                            self.menu.current_state = "main_menu"
                        elif self.menu.current_state == "title":
                            # From title screen, ESC should exit the game
                            self.running = False
                    else:
                        self.running = False
                
                elif event.key == pygame.K_SPACE and self.game_state == "playing":
                    # Try to collect from shelf or deliver
                    self._handle_space_key()
                
                elif event.key == pygame.K_p and self.game_state == "playing":
                    # Toggle pause
                    self.game_state = "paused" if self.game_state == "playing" else "playing"
                    self._show_message("Game Paused" if self.game_state == "paused" else "Game Resumed")
                
                elif event.key == pygame.K_r and self.game_state == "game_over":
                    # Restart game
                    self.level = 1
                    self.score = 0
                    self._setup_level()
                    self.game_state = "playing"
                
                elif event.key == pygame.K_n and self.game_state == "level_complete":
                    # Next level
                    self.level += 1
                    self._setup_level()
                    self.game_state = "playing"
        
        # Handle menu interactions
        if self.game_state == "menu":
            # First handle events (for title screen)
            menu_event_result = self.menu.handle_events(events)
            
            # Then update menu with current mouse state
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            menu_update_result = self.menu.update(mouse_pos, mouse_pressed)
            
            # Process results
            if menu_update_result == "play":
                print("Play button pressed, setting up level...")
                self._setup_level()
                self.game_state = "playing"
            elif menu_update_result == "toggle_fullscreen":
                self._toggle_fullscreen()
        
        return True
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        if self.fullscreen:
            # Switch to windowed
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.fullscreen = False
        else:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            self.fullscreen = True
        
        print(f"   Display mode changed to {'fullscreen' if self.fullscreen else 'windowed'}")
    
    def _handle_space_key(self):
        """Handle space key to collect or deliver items."""
        # First, check if player is in a delivery zone
        grid_pos = self.player.get_grid_position(self.warehouse)
        if grid_pos:
            grid_x, grid_y = grid_pos
            if self.warehouse.get_cell_type(grid_x, grid_y) == CellType.DELIVERY:
                # Try to deliver items that match the order
                delivered = self._try_deliver()
                if delivered > 0:
                    self._show_message(f"Delivered: {delivered} items!")
                    self.score += delivered * 10
                    self.audio_manager.play_sound("deliver_sound")
                    
                    # Check if order is complete
                    if self._is_order_complete():
                        self.game_state = "level_complete"
                        self.score += int(self.time_remaining) * 5  # Bonus points for remaining time
                        self._show_message(f"Level {self.level} Complete! Press N for next level")
                    return
                else:
                    self._show_message("No deliverable items in inventory")
                    return
        
        # If not at delivery, try to pick from adjacent shelf
        if self.player.try_pick_from_shelf(self.warehouse):
            self._show_message("Product collected!")
            self.audio_manager.play_sound("pickup_sound")
        else:
            # Check why it failed
            shelf_pos = self.player.get_adjacent_shelf(self.warehouse)
            if shelf_pos:
                grid_x, grid_y = shelf_pos
                if self.warehouse.get_shelf_quantity(grid_x, grid_y) == 0:
                    self._show_message("Empty shelf")
                elif not self.player.can_pick_up():
                    self._show_message("Inventory full")
            else:
                self._show_message("No shelves nearby")
    
    def _try_deliver(self):
        """Try to deliver items from player's inventory that match the order."""
        delivered = 0
        
        # Create a copy of inventory to iterate while modifying
        for item in self.player.inventory[:]:
            for order in self.orders:
                if order['product'] == item and order['collected'] < order['quantity']:
                    if self.player.deliver_product(item):
                        order['collected'] += 1
                        delivered += 1
                        break
            else:
                # Item is not in order
                self._show_message(f"{item.value} not in current order")
        
        return delivered
    
    def _is_order_complete(self):
        """Check if current order is complete."""
        for order in self.orders:
            if order['collected'] < order['quantity']:
                return False
        return True
    
    def _check_ai_progress(self):
        """Check if any AI has completed the order (DELIVERED ALL ITEMS)."""
        for ai in self.ai_pickers:
            if ai.is_order_complete():
                print(f"AI has completed the order! Game over for player.")
                self.game_state = "game_over"
                self._show_message("AI completed the order first! Game Over")
                return True
        return False
    
    def _update_timer(self, delta_time):
        """Update the level timer."""
        if self.game_state == "playing":
            self.time_remaining -= delta_time
            
            # Check if time ran out
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_state = "game_over"
                self._show_message("Time's up! Game Over")
            
            # Check if AI completed order
            self._check_ai_progress()
    
    def _show_message(self, text):
        """Show a temporary message on screen."""
        self.message = text
        self.message_timer = 2.0  # Show for 2 seconds
    
    def handle_movement(self):
        """Handle player movement based on keyboard input."""
        keys = pygame.key.get_pressed()
        
        # Calculate movement direction
        dx, dy = 0, 0
        
        # Arrow keys and WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Move player
        if dx != 0 or dy != 0:
            self.player.move_with_collision(dx, dy, self.warehouse, 
                                           SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def update(self, delta_time):
        """Update game logic."""
        if self.game_state == "menu" or self.game_state == "paused":
            return
        
        if self.game_state == "playing":
            # Update timer
            self._update_timer(delta_time)
            
            # Handle continuous movement
            self.handle_movement()
            
            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= delta_time
                if self.message_timer <= 0:
                    self.message = ""
            
            # Update AI pickers
            for ai in self.ai_pickers:
                delivered = ai.update(delta_time, self.player)
                if delivered > 0:
                    self._show_message(f"AI delivered {delivered} items")
                    # Check if AI completed order after delivery
                    self._check_ai_progress()
    
    def draw(self):
        """Draw everything on screen."""
        if self.game_state == "menu":
            self.menu.draw(self.screen)
        else:
            # Draw game screen
            self.screen.fill(BACKGROUND)
            
            # Draw warehouse
            if self.warehouse:
                self.warehouse.draw(self.screen)
            
            # Draw player
            if self.player:
                self.player.draw(self.screen)
            
            # Draw AI pickers
            for ai in self.ai_pickers:
                ai.draw(self.screen)
            
            # Draw UI
            self._draw_ui()
            
            # Draw message
            if self.message:
                text = self.font.render(self.message, True, HIGHLIGHT)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                self.screen.blit(text, text_rect)
            
            # Draw game over or level complete screen
            if self.game_state == "game_over":
                self._draw_game_over()
            elif self.game_state == "level_complete":
                self._draw_level_complete()
            elif self.game_state == "paused":
                self._draw_paused()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw user interface elements."""
        # Draw score and level
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 20))
        
        # Draw timer with color coding
        minutes = int(self.time_remaining) // 60
        seconds = int(self.time_remaining) % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        
        # Change color based on remaining time
        if self.time_remaining > 60:
            time_color = GREEN
        elif self.time_remaining > 30:
            time_color = YELLOW
        else:
            time_color = RED
        
        timer_text = self.font.render(time_text, True, time_color)
        self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        # Draw Current Order (right side, below level)
        order_x = SCREEN_WIDTH - 180
        order_y = 100  # below level

        title_text = self.font.render("Current Order", True, TEXT_COLOR)
        self.screen.blit(title_text, (order_x, order_y))

        for i, order in enumerate(self.orders):
            product_name = order['product'].value.capitalize()
            text = f"{product_name}: {order['collected']}/{order['quantity']}"
            color = GREEN if order['collected'] >= order['quantity'] else TEXT_COLOR

            order_text = self.small_font.render(text, True, color)
            self.screen.blit(order_text, (order_x, order_y + 30 + i * 22))

        
        # Draw player inventory
        inv_text = self.font.render(f"Inventory: {len(self.player.inventory)}/{self.player.max_capacity}", 
                                   True, TEXT_COLOR)
        self.screen.blit(inv_text, (20, SCREEN_HEIGHT - 60))
        
        # Draw controls
        controls = [
            "Controls:",
            "WASD/Arrows - Move",
            "SPACE - Collect",
            "P - Pause",
            "ESC - Menu"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, TEXT_COLOR)
            self.screen.blit(control_text, (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 150 + i * 25))
    
    def _draw_game_over(self):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 100))
        
        # Reason
        if self.time_remaining <= 0:
            reason_text = self.font.render("Time's up!", True, TEXT_COLOR)
        else:
            reason_text = self.font.render("AI completed the order first!", True, TEXT_COLOR)
        
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30))
        
        # Final score
        score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        
        # Level reached
        level_text = self.font.render(f"Level Reached: {self.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60))
        
        # Restart instructions
        restart_text = self.small_font.render("Press R to Restart or ESC for Menu", True, HIGHLIGHT)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 120))
    
    def _draw_level_complete(self):
        """Draw level complete screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 50, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Level complete text
        complete_text = self.big_font.render("LEVEL COMPLETE!", True, GREEN)
        self.screen.blit(complete_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
        
        # Time bonus
        bonus = int(self.time_remaining) * 5
        bonus_text = self.font.render(f"Time Bonus: +{bonus} points", True, YELLOW)
        self.screen.blit(bonus_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 30))
        
        # Total score
        total_score = self.score + bonus
        score_text = self.font.render(f"Total Score: {total_score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20))
        
        # Next level instructions
        next_text = self.small_font.render("Press N for Next Level or ESC for Menu", True, HIGHLIGHT)
        self.screen.blit(next_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 80))
    
    def _draw_paused(self):
        """Draw pause screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.big_font.render("PAUSED", True, YELLOW)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
        
        # Instructions
        continue_text = self.font.render("Press P to Continue", True, TEXT_COLOR)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 30))
    
    def run(self):
        """Main game loop."""
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(delta_time)
            
            # Draw everything
            self.draw()
            
            # Limit framerate
            self.clock.tick(FPS)
        
        # Save audio settings before quitting
        self.audio_manager.save_settings()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = Game()
        print("Game initialized successfully")
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)