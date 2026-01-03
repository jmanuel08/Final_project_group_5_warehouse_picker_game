"""
Player class for the warehouse picker game.
Handles movement, inventory, and interaction with the warehouse.
"""

import pygame
from src.warehouse import CellType

class Player:
    """Player-controlled picker."""
    
    def __init__(self, x, y, asset_loader=None):
        self.x = x
        self.y = y
        self.speed = 3
        self.size = 32
        
        # Sprite
        self.assets = asset_loader.assets if asset_loader else {}
        self.sprite = self.assets.get("player")
        if not self.sprite:
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            self.sprite.fill((50, 200, 50, 255))  # Green color for player
        
        # Inventory
        self.inventory = []
        self.max_capacity = 5  # Increased capacity
        
        print("   ✓ Player created")
    
    def move_with_collision(self, dx, dy, warehouse, screen_width, screen_height):
        """Move player with simplified collision detection."""
        if dx == 0 and dy == 0:
            return
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071
        
        # Calculate new position
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Check screen boundaries
        padding = 50
        if new_x < padding or new_x > screen_width - padding - self.size:
            new_x = self.x
        if new_y < padding or new_y > screen_height - padding - self.size:
            new_y = self.y
        
        # Simple collision check with warehouse
        if warehouse:
            # Get grid position of player center
            center_x = new_x + self.size // 2
            center_y = new_y + self.size // 2
            grid_pos = warehouse.get_cell_at_pixel(center_x, center_y)
            
            if grid_pos:
                grid_x, grid_y = grid_pos
                cell_type = warehouse.get_cell_type(grid_x, grid_y)
                
                # Only prevent movement into walls
                if cell_type and cell_type.value == "wall":
                    # Try to move only in x or y direction
                    if dx != 0:
                        # Try moving only in x
                        temp_x = self.x + dx * self.speed
                        temp_y = self.y
                        center_x = temp_x + self.size // 2
                        center_y = temp_y + self.size // 2
                        grid_pos = warehouse.get_cell_at_pixel(center_x, center_y)
                        if grid_pos:
                            grid_x, grid_y = grid_pos
                            cell_type = warehouse.get_cell_type(grid_x, grid_y)
                            if cell_type and cell_type.value != "wall":
                                self.x = temp_x
                                return
                    
                    if dy != 0:
                        # Try moving only in y
                        temp_x = self.x
                        temp_y = self.y + dy * self.speed
                        center_x = temp_x + self.size // 2
                        center_y = temp_y + self.size // 2
                        grid_pos = warehouse.get_cell_at_pixel(center_x, center_y)
                        if grid_pos:
                            grid_x, grid_y = grid_pos
                            cell_type = warehouse.get_cell_type(grid_x, grid_y)
                            if cell_type and cell_type.value != "wall":
                                self.y = temp_y
                                return
                    
                    # Can't move in either direction
                    return
            
            # If no collision with wall, allow movement
            self.x = new_x
            self.y = new_y
        else:
            self.x = new_x
            self.y = new_y
    
    def can_pick_up(self):
        """Check if player can pick up more items."""
        return len(self.inventory) < self.max_capacity
    
    def pick_up_product(self, product):
        """Pick up a product and add it to inventory."""
        if self.can_pick_up():
            self.inventory.append(product)
            return True
        return False
    
    def deliver_product(self, product):
        """Deliver a product from inventory."""
        if product in self.inventory:
            self.inventory.remove(product)
            return True
        return False
    
    def get_grid_position(self, warehouse):
        """Get player's current grid position."""
        if warehouse:
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            return warehouse.get_cell_at_pixel(center_x, center_y)
        return None
    
    def get_adjacent_shelf(self, warehouse):
        """Get the grid position of a shelf adjacent to the player."""
        grid_pos = self.get_grid_position(warehouse)
        if not grid_pos:
            return None
        
        grid_x, grid_y = grid_pos
        
        # Check all 8 directions around the player
        directions = [
            (0, -1),   # Up
            (1, -1),   # Up-right
            (1, 0),    # Right
            (1, 1),    # Down-right
            (0, 1),    # Down
            (-1, 1),   # Down-left
            (-1, 0),   # Left
            (-1, -1)   # Up-left
        ]
        
        for dx, dy in directions:
            check_x, check_y = grid_x + dx, grid_y + dy
            if warehouse.get_cell_type(check_x, check_y) == CellType.SHELF:
                # Check if shelf has products
                if warehouse.get_shelf_quantity(check_x, check_y) > 0:
                    return (check_x, check_y)
        
        return None
    
    def try_pick_from_shelf(self, warehouse):
        """Try to pick up a product from an adjacent shelf."""
        shelf_pos = self.get_adjacent_shelf(warehouse)
        if shelf_pos:
            grid_x, grid_y = shelf_pos
            product = warehouse.take_product(grid_x, grid_y)
            if product:
                return self.pick_up_product(product)
        return False
    
    def draw(self, screen):
        """Draw the player on screen."""
        # Draw sprite
        if self.sprite:
            scaled_sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
            screen.blit(scaled_sprite, (self.x, self.y))
        else:
            # Fallback: draw a green rectangle with border
            pygame.draw.rect(screen, (50, 200, 50), 
                           (self.x, self.y, self.size, self.size))
            pygame.draw.rect(screen, (30, 180, 30), 
                           (self.x, self.y, self.size, self.size), 2)
            
            # Draw "P" for player
            font = pygame.font.Font(None, 24)
            text = font.render("P", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
            screen.blit(text, text_rect)
        
        # Draw inventory indicator
        if self.inventory:
            # Draw inventory slots above player
            # INCREASE SLOT SIZE: from 16 to 20 pixels
            slot_size = 20  # Changed from 16 to 20
            slot_spacing = 4  # Slightly increase spacing
            start_x = self.x + (self.size - (self.max_capacity * (slot_size + slot_spacing) - slot_spacing)) // 2
            
            for i in range(self.max_capacity):
                slot_x = start_x + i * (slot_size + slot_spacing)
                slot_y = self.y - slot_size - 5
                
                # Draw slot background
                pygame.draw.rect(screen, (50, 50, 50), 
                               (slot_x, slot_y, slot_size, slot_size))
                pygame.draw.rect(screen, (100, 100, 100), 
                               (slot_x, slot_y, slot_size, slot_size), 1)
                
                # Draw item if present
                if i < len(self.inventory):
                    product_color = self._get_product_color(self.inventory[i])
                    # Increase item size within slot
                    item_padding = 3  # Reduce padding for larger item
                    pygame.draw.rect(screen, product_color, 
                                   (slot_x + item_padding, slot_y + item_padding, 
                                    slot_size - item_padding * 2, slot_size - item_padding * 2))
            
            # Draw item count
            font = pygame.font.Font(None, 18)
            text = font.render(f"{len(self.inventory)}/{self.max_capacity}", True, (255, 255, 255))
            screen.blit(text, (self.x + self.size + 5, self.y))
    
    def _get_product_color(self, product):
        """Get color for a product type."""
        colors = {
            "bread": (210, 180, 140),
            "eggs": (255, 255, 240),
            "milk": (240, 240, 255),
            "chocolate": (101, 67, 33),
            "apples": (255, 50, 50),
            "toilet_paper": (255, 255, 230),
            "chips": (255, 200, 50)
        }
        return colors.get(product.value, (200, 200, 200))