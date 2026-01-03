"""
AI Picker class - Basic AI opponent.
"""

import pygame
import random
import math
from src.warehouse import CellType, ProductType

class AIPicker:
    """Basic AI picker that collects products."""
    
    def __init__(self, x, y, warehouse, asset_loader=None, difficulty_level=1):
        self.x = x
        self.y = y
        self.warehouse = warehouse
        self.difficulty_level = difficulty_level
        
        # Movement
        self.speed = 1.8 + (difficulty_level * 0.3)  # Adjusted speed
        self.size = 32
        
        # Sprite
        self.assets = asset_loader.assets if asset_loader else {}
        self.sprite = self.assets.get("ai")
        if not self.sprite:
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            self.sprite.fill((200, 50, 50, 255))  # Red color for AI
        
        # Inventory
        self.inventory = []
        self.max_capacity = 3 + difficulty_level  # Capacity increases with difficulty
        
        # AI state machine
        self.state = "idle"  # idle, moving_to_shelf, at_shelf, moving_to_delivery, delivering
        self.target_shelf = None
        self.target_delivery = None
        
        # Action timing
        self.action_timer = 0.0
        self.pick_time = 1.0  # Time to pick an item
        self.deliver_time = 1.0  # Time to deliver
        
        # Current order tracking
        self.current_order = []
        self.order_progress = {}
        self.items_to_deliver = {}  # Items that still need to be delivered
        
        # Avoidance
        self.avoid_player = True
        self.last_player_pos = None
        
        # Movement helpers
        self.move_dx = 0
        self.move_dy = 0
        
        # Stuck detection
        self.stuck_counter = 0
        self.max_stuck_attempts = 10
        self.last_positions = []
        
        print(f"   ✓ AI created (Level {difficulty_level}, Speed: {self.speed:.1f}, Capacity: {self.max_capacity})")
    
    def reset_state(self):
        """Reset AI state to initial conditions."""
        self.state = "idle"
        self.target_shelf = None
        self.target_delivery = None
        self.action_timer = 0
        self.inventory = []
        self.current_order = []
        self.order_progress = {}
        self.items_to_deliver = {}
        self.last_player_pos = None
        self.move_dx = 0
        self.move_dy = 0
        self.stuck_counter = 0
        self.last_positions = []
    
    def can_pick_up(self):
        """Check if AI can pick up more items."""
        return len(self.inventory) < self.max_capacity
    
    def assign_order(self, order_items):
        """Assign an order to the AI."""
        self.current_order = order_items
        self.order_progress = {}
        self.items_to_deliver = {}
        
        for item in order_items:
            product = item['product']
            self.order_progress[product] = {
                'needed': item['quantity'],
                'collected': 0,
                'delivered': 0
            }
            self.items_to_deliver[product] = item['quantity']  # Items that need to be delivered
        
        print(f"AI assigned order: {[(p.value, d['needed']) for p, d in self.order_progress.items()]}")
    
    def is_order_complete(self):
        """Check if AI has completed its order (ALL ITEMS DELIVERED)."""
        if not self.order_progress:
            return False
            
        for product, progress in self.order_progress.items():
            if progress['delivered'] < progress['needed']:
                return False
        return True
    
    def update(self, delta_time, player=None):
        """Update AI state and movement."""
        self.action_timer += delta_time
        
        # Track player position for avoidance
        if player:
            self.last_player_pos = (player.x, player.y)
        
        # State machine
        if self.state == "idle":
            self._decide_next_action()
        
        elif self.state == "moving_to_shelf":
            self._move_to_shelf_simple()
        
        elif self.state == "at_shelf":
            if self.action_timer >= self.pick_time:
                success = self._pick_item()
                if success:
                    print(f"AI picked item. Inventory: {len(self.inventory)}/{self.max_capacity}")
                self.state = "idle"
                self.stuck_counter = 0
        
        elif self.state == "moving_to_delivery":
            self._move_to_delivery_simple()
        
        elif self.state == "delivering":
            if self.action_timer >= self.deliver_time:
                delivered_items = self._deliver_items()
                self.state = "idle"
                self.stuck_counter = 0
                return delivered_items  # Return number of items delivered
        
        return 0
    
    def simple_move(self, target_x, target_y):
        """Simple movement without complex collision detection."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            # Calculate new position
            new_x = self.x + dx_normalized * self.speed
            new_y = self.y + dy_normalized * self.speed
            
            # Store current position for stuck detection
            self.last_positions.append((self.x, self.y))
            if len(self.last_positions) > 10:
                self.last_positions.pop(0)
            
            # Check if we're stuck (not moving much)
            if len(self.last_positions) >= 5:
                total_movement = 0
                for i in range(1, len(self.last_positions)):
                    prev_x, prev_y = self.last_positions[i-1]
                    curr_x, curr_y = self.last_positions[i]
                    total_movement += math.sqrt((curr_x-prev_x)**2 + (curr_y-prev_y)**2)
                
                if total_movement < 10:  # Hardly moved in last 5 frames
                    self.stuck_counter += 1
                    if self.stuck_counter > self.max_stuck_attempts:
                        print(f"AI stuck at ({self.x:.0f}, {self.y:.0f}), resetting...")
                        self.state = "idle"
                        self.stuck_counter = 0
                        self.last_positions = []
                        return False
            
            # Move to new position
            self.x = new_x
            self.y = new_y
            
            # Check if reached target
            new_distance = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
            return new_distance < 30  # Return True if reached
        
        return False
    
    def _decide_next_action(self):
        """Decide what the AI should do next."""
        # First, check if we have items to deliver
        if self._has_items_to_deliver():
            print("AI has items to deliver, going to delivery")
            self._go_to_delivery()
            return
        
        # If inventory is full, go deliver
        if len(self.inventory) >= self.max_capacity:
            print("AI inventory full, going to delivery")
            self._go_to_delivery()
            return
        
        # If we have an order, find a shelf with needed product
        needed_product = self._get_needed_product()
        if needed_product:
            shelf_pos = self._find_shelf_with_product(needed_product)
            if shelf_pos:
                self._go_to_shelf(shelf_pos)
                return
        
        # Otherwise, go to a random shelf that has products
        print("AI going to random shelf")
        self._go_to_random_shelf()
    
    def _has_items_to_deliver(self):
        """Check if AI has items in inventory that need to be delivered."""
        # Check if any item in inventory is needed for delivery
        for item in self.inventory:
            if item in self.items_to_deliver and self.items_to_deliver[item] > 0:
                return True
        return False
    
    def _get_needed_product(self):
        """Get a product that is still needed for the order (not yet collected enough)."""
        if not self.order_progress:
            return None
        
        for product, progress in self.order_progress.items():
            # We need more of this product if collected < needed
            if progress['collected'] < progress['needed']:
                return product
        return None
    
    def _find_shelf_with_product(self, product):
        """Find a shelf that contains the specified product."""
        available_shelves = []
        for (col, row), shelf_info in self.warehouse.shelf_products.items():
            if shelf_info['type'] == product and shelf_info['quantity'] > 0:
                available_shelves.append((col, row))
        
        if not available_shelves:
            return None
        
        # Choose the closest shelf using Manhattan distance
        ai_grid_pos = self.warehouse.get_cell_at_pixel(self.x, self.y)
        if not ai_grid_pos:
            return random.choice(available_shelves)
        
        ai_x, ai_y = ai_grid_pos
        closest = None
        min_distance = float('inf')
        
        for (col, row) in available_shelves:
            distance = abs(col - ai_x) + abs(row - ai_y)  # Manhattan distance
            if distance < min_distance:
                min_distance = distance
                closest = (col, row)
        
        return closest
    
    def _go_to_shelf(self, shelf_pos):
        """Set path to a shelf."""
        self.target_shelf = shelf_pos
        self.state = "moving_to_shelf"
        self.action_timer = 0
        self.stuck_counter = 0
        self.last_positions = []
        print(f"AI going to shelf at {shelf_pos}")
    
    def _go_to_random_shelf(self):
        """Go to a random shelf that has products."""
        available_shelves = []
        for (col, row), info in self.warehouse.shelf_products.items():
            if info['quantity'] > 0:
                available_shelves.append((col, row))
        
        if available_shelves:
            shelf_pos = random.choice(available_shelves)
            self._go_to_shelf(shelf_pos)
        else:
            # No shelves with products, go to delivery
            print("No shelves available, going to delivery")
            self._go_to_delivery()
    
    def _go_to_delivery(self):
        """Go to the delivery zone."""
        if self.warehouse.delivery_zones:
            # Get current grid position
            ai_grid_pos = self.warehouse.get_cell_at_pixel(self.x, self.y)
            if ai_grid_pos:
                ai_x, ai_y = ai_grid_pos
                # Find nearest delivery (but there should be only one now)
                if self.warehouse.delivery_zones:
                    self.target_delivery = self.warehouse.delivery_zones[0]  # Only one delivery zone
                    self.state = "moving_to_delivery"
                    self.action_timer = 0
                    self.stuck_counter = 0
                    self.last_positions = []
                    print(f"AI going to delivery at {self.target_delivery}")
                    return
        
        # Fallback
        print("No delivery zone found, going idle")
        self.state = "idle"
    
    def _move_to_shelf_simple(self):
        """Simple movement towards shelf."""
        if self.target_shelf:
            target_x, target_y = self.warehouse.get_pixel_position(*self.target_shelf)
            reached = self.simple_move(target_x, target_y)
            
            if reached:
                self.state = "at_shelf"
                self.action_timer = 0
                print(f"AI reached shelf at {self.target_shelf}")
    
    def _move_to_delivery_simple(self):
        """Simple movement towards delivery zone."""
        if self.target_delivery:
            target_x, target_y = self.warehouse.get_pixel_position(*self.target_delivery)
            reached = self.simple_move(target_x, target_y)
            
            if reached:
                self.state = "delivering"
                self.action_timer = 0
                print("AI reached delivery zone")
    
    def _pick_item(self):
        """Pick an item from the current shelf."""
        if self.target_shelf and self.can_pick_up():
            col, row = self.target_shelf
            product = self.warehouse.take_product(col, row)
            
            if product:
                self.inventory.append(product)
                
                # Update order progress - only if this product is in our order
                if product in self.order_progress:
                    self.order_progress[product]['collected'] += 1
                    print(f"AI collected {product.value}. Collected: {self.order_progress[product]['collected']}/{self.order_progress[product]['needed']}")
                
                return True
            else:
                print(f"AI failed to pick from shelf at {self.target_shelf}")
        
        return False
    
    def _deliver_items(self):
        """Deliver items in inventory that are in the order."""
        delivered_count = 0
        
        # Check each item in inventory against order
        items_to_remove = []
        for product in self.inventory:
            if (product in self.order_progress and 
                product in self.items_to_deliver and 
                self.items_to_deliver[product] > 0):
                
                # Deliver this item
                self.order_progress[product]['delivered'] += 1
                self.items_to_deliver[product] -= 1
                delivered_count += 1
                items_to_remove.append(product)
                print(f"AI delivered {product.value}. Delivered: {self.order_progress[product]['delivered']}/{self.order_progress[product]['needed']}")
        
        # Remove delivered items from inventory
        for product in items_to_remove:
            self.inventory.remove(product)
        
        print(f"AI delivered {delivered_count} items. Inventory: {len(self.inventory)}/{self.max_capacity}")
        
        # Check if order is now complete
        if self.is_order_complete():
            print("AI HAS COMPLETED THE ENTIRE ORDER!")
        
        return delivered_count
    
    def draw(self, screen):
        """Draw the AI picker."""
        # Draw sprite
        if self.sprite:
            scaled_sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
            screen.blit(scaled_sprite, (self.x - self.size//2, self.y - self.size//2))
        else:
            # Fallback: draw a red rectangle with border
            pygame.draw.rect(screen, (200, 50, 50), 
                           (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
            pygame.draw.rect(screen, (180, 30, 30), 
                           (self.x - self.size//2, self.y - self.size//2, self.size, self.size), 2)
            
            # Draw "AI" text
            font = pygame.font.Font(None, 20)
            text = font.render("AI", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)
        
        # Draw inventory indicator
        if self.inventory:
            font = pygame.font.Font(None, 18)
            text = font.render(f"{len(self.inventory)}/{self.max_capacity}", True, (255, 255, 255))
            screen.blit(text, (self.x + self.size//2, self.y - self.size//2))
        
        # Draw state indicator (for debugging)
        font = pygame.font.Font(None, 16)
        state_text = font.render(f"State: {self.state}", True, (255, 255, 200))
        screen.blit(state_text, (self.x - self.size//2, self.y + self.size//2 + 5))