"""
Warehouse class for the warehouse picker game.
Represents the grid-based warehouse with shelves and products.
"""

import pygame
pygame.font.init()

import random
import time
from enum import Enum

class CellType(Enum):
    """Types of cells in the warehouse grid."""
    AISLE = "aisle"      # Walkable area
    SHELF = "shelf"      # Shelf with products (not walkable)
    DELIVERY = "delivery"  # Delivery zone
    WALL = "wall"        # Wall (not walkable)
    EMPTY = "empty"      # Empty space

class ProductType(Enum):
    """Types of products that can be on shelves."""
    BREAD = "bread"
    EGGS = "eggs"
    MILK = "milk"
    CHOCOLATE = "chocolate"
    APPLES = "apples"
    TOILET_PAPER = "toilet_paper"
    CHIPS = "chips"


class Warehouse:
    """Warehouse grid system with supermarket products."""
    
    def __init__(self, x_offset=0, y_offset=0, width=15, height=15, cell_size=64, 
                 asset_loader=None, level=1, required_products=None):
        """
        Initialize warehouse.
        
        Args:
            x_offset: X position on screen where warehouse starts
            y_offset: Y position on screen where warehouse starts  
            width: Number of cells horizontally
            height: Number of cells vertically
            cell_size: Size of each cell in pixels
            asset_loader: AssetLoader instance with loaded sprites
            level: Current game level (affects layout)
            required_products: List of ProductType that must be present in the warehouse
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.level = level
        self.required_products = required_products if required_products else []
        
        # Store asset loader
        self.assets = asset_loader.assets if asset_loader else {}
        
        # Create the grid
        self.grid = []
        self.shelf_products = {}  # Dictionary to store products at shelf positions
        
        # Delivery zone positions (now only 1 per level)
        self.delivery_zones = []
        
        # Track product counts for max 2 shelves per product
        self.product_counts = {product_type: 0 for product_type in ProductType}
        
        print(f"   Generating warehouse layout...")
        start_time = time.time()
        
        try:
            self._generate_layout()
            elapsed = time.time() - start_time
            print(f"   ✓ Warehouse created in {elapsed:.2f} seconds")
            print(f"   ✓ Size: {width}x{height} cells (Level {level})")
            print(f"   ✓ Delivery zones: {len(self.delivery_zones)}")
            print(f"   ✓ Total shelves: {len(self.shelf_products)}")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ✗ Error creating warehouse after {elapsed:.2f} seconds: {e}")
            import traceback
            traceback.print_exc()
            # Create a minimal warehouse as fallback
            self._create_minimal_fallback()
    
    def _create_minimal_fallback(self):
        """Create a minimal warehouse as fallback."""
        print("   Creating minimal fallback warehouse...")
        
        # Start with all aisle cells
        self.grid = [[CellType.AISLE for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        # Add walls around the edges
        for row in range(self.height):
            self.grid[row][0] = CellType.WALL
            self.grid[row][self.width - 1] = CellType.WALL
        for col in range(self.width):
            self.grid[0][col] = CellType.WALL
            self.grid[self.height - 1][col] = CellType.WALL
        
        # Place 2 shelves for each required product
        for product in self.required_products[:2]:  # Max 2 products
            for i in range(2):  # 2 shelves per product
                x = 2 + i * 3
                y = 2
                if x < self.width - 1 and y < self.height - 1:
                    self.grid[y][x] = CellType.SHELF
                    self.shelf_products[(x, y)] = {
                        'type': product,
                        'quantity': 3
                    }
        
        # Place delivery zone in the middle
        delivery_x = self.width // 2
        delivery_y = self.height // 2
        self.grid[delivery_y][delivery_x] = CellType.DELIVERY
        self.delivery_zones.append((delivery_x, delivery_y))
        
        print("   ✓ Minimal fallback warehouse created")
    
    def _generate_layout(self):
        """Generate the warehouse grid layout with controlled shelf placement."""
        # Start with all aisle cells
        self.grid = [[CellType.AISLE for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        # Add walls around the edges
        for row in range(self.height):
            self.grid[row][0] = CellType.WALL
            self.grid[row][self.width - 1] = CellType.WALL
        for col in range(self.width):
            self.grid[0][col] = CellType.WALL
            self.grid[self.height - 1][col] = CellType.WALL
        
        print(f"   Placing required products...")
        # First, place required products to ensure they exist
        required_placed = self._place_required_products()
        print(f"   Placed {required_placed} required shelves")
        
        print(f"   Placing remaining shelves...")
        # Place other shelves (max 2 per product type)
        self._place_remaining_shelves()
        
        print(f"   Placing delivery zone...")
        # Create exactly ONE delivery zone
        self._place_single_delivery_zone()
    
    def _place_required_products(self):
        """Place shelves for required products. Returns number of shelves placed."""
        placed_count = 0
        
        for product in self.required_products:
            # Try to place up to 2 shelves for this required product
            shelves_to_place = min(2, 2 - self.product_counts[product])
            for _ in range(shelves_to_place):
                if self.product_counts[product] >= 2:
                    break  # Already have 2 shelves of this product
                    
                placed = False
                attempts = 0
                
                while not placed and attempts < 50:  # Limit attempts
                    x = random.randint(1, self.width - 2)
                    y = random.randint(1, self.height - 2)
                    
                    # Check if cell is walkable and not adjacent to another shelf
                    if self.grid[y][x] == CellType.AISLE and self._is_valid_shelf_position(x, y):
                        # Place the shelf
                        self.grid[y][x] = CellType.SHELF
                        self.shelf_products[(x, y)] = {
                            'type': product,
                            'quantity': random.randint(3, 6),
                            'owner': 'player'  # More items for required products
                         }
                        self.product_counts[product] += 1
                        placed = True
                        placed_count += 1
                    
                    attempts += 1
                
                if not placed:
                    print(f"   ⚠️ Could not place shelf for {product.value} after 50 attempts")
        
        return placed_count
    
    def _place_remaining_shelves(self):
        """Place remaining shelves with max 2 per product type."""
        # Calculate how many shelves we can place
        max_shelves = min(10 + self.level * 2, 20)
        placed_shelves = sum(self.product_counts.values())
        
        # List of products that can still have shelves
        available_products = [p for p in ProductType if self.product_counts[p] < 2]
        
        print(f"   Target shelves: {max_shelves}, Current: {placed_shelves}")
        
        attempts = 0
        while placed_shelves < max_shelves and available_products and attempts < 100:
            # Choose a product that needs more shelves
            product = random.choice(available_products)
            
            placed = False
            shelf_attempts = 0
            
            while not placed and shelf_attempts < 20:
                x = random.randint(2, self.width - 3)  # Keep away from walls
                y = random.randint(2, self.height - 3)
                
                # Check if cell is walkable and valid for shelf
                if self.grid[y][x] == CellType.AISLE and self._is_valid_shelf_position(x, y):
                    # Place the shelf
                    self.grid[y][x] = CellType.SHELF
                    self.shelf_products[(x, y)] = {
                        'type': product,
                        'quantity': random.randint(2, 5),
                        'owner': 'ai'
                     }
                    self.product_counts[product] += 1
                    placed = True
                    placed_shelves += 1
                
                shelf_attempts += 1
            
            # Update available products
            available_products = [p for p in ProductType if self.product_counts[p] < 2]
            attempts += 1
        
        print(f"   Finished with {placed_shelves} shelves")
    
    def _is_valid_shelf_position(self, x, y):
        """Check if a position is valid for placing a shelf."""
        # Simple check - just make sure not too close to walls
        return (x > 1 and x < self.width - 2 and 
                y > 1 and y < self.height - 2)
    
    def _place_single_delivery_zone(self):
        """Place exactly ONE delivery zone."""
        placed = False
        attempts = 0
        
        while not placed and attempts < 100:
            x = random.randint(3, self.width - 4)
            y = random.randint(3, self.height - 4)
            
            if self.grid[y][x] == CellType.AISLE:
                # Simple check - just make sure it's not too close to walls
                self.grid[y][x] = CellType.DELIVERY
                self.delivery_zones.append((x, y))
                placed = True
                print(f"   ✓ Delivery zone placed at ({x}, {y})")
            
            attempts += 1
        
        if not placed:
            # Fallback: place in the middle
            x, y = self.width // 2, self.height // 2
            self.grid[y][x] = CellType.DELIVERY
            self.delivery_zones.append((x, y))
            print(f"   ⚠️ Delivery zone placed at default position ({x}, {y})")
    
    def get_cell_type(self, grid_x, grid_y):
        """Get the type of cell at grid coordinates."""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x]
        return None
    
    def get_cell_at_pixel(self, pixel_x, pixel_y):
        """Convert pixel coordinates to grid coordinates."""
        grid_x = (pixel_x - self.x_offset) // self.cell_size
        grid_y = (pixel_y - self.y_offset) // self.cell_size
        
        # Make sure they are integers
        grid_x = int(grid_x)
        grid_y = int(grid_y)
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return (grid_x, grid_y)
        return None
    
    def get_pixel_position(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates (center of cell)."""
        pixel_x = self.x_offset + grid_x * self.cell_size + self.cell_size // 2
        pixel_y = self.y_offset + grid_y * self.cell_size + self.cell_size // 2
        return (pixel_x, pixel_y)
    
    def is_walkable(self, grid_x, grid_y):
        """Check if a cell is walkable."""
        cell_type = self.get_cell_type(grid_x, grid_y)
        return cell_type in [CellType.AISLE, CellType.DELIVERY]
    
    def get_random_walkable_position(self):
        """Get a random walkable position in the warehouse."""
        walkable_cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.is_walkable(col, row):
                    walkable_cells.append((col, row))
        
        if not walkable_cells:
            # Fallback: return a default position
            return self.get_pixel_position(1, 1)
        
        # Choose a random walkable cell
        col, row = random.choice(walkable_cells)
        return self.get_pixel_position(col, row)
    
    def has_product_available(self, product_type):
        """Check if a product type is available in any shelf."""
        for shelf_info in self.shelf_products.values():
            if shelf_info['type'] == product_type and shelf_info['quantity'] > 0:
                return True
        return False
    
    def take_product(self, x, y, picker="player"):
        shelf = self.shelf_products.get((x, y))
        if not shelf:
            return None

        # BLOCK wrong owner
        if shelf.get("owner") != picker:
            return None

        if shelf["quantity"] > 0:
            shelf["quantity"] -= 1
            return shelf["type"]
        return None

    

    #def take_product(self, grid_x, grid_y):
    #    """Take one product from a shelf. Returns product type if successful, None otherwise."""
    #    grid_x = int(grid_x)
    #    grid_y = int(grid_y)
    #    
    #    if self.get_cell_type(grid_x, grid_y) == CellType.SHELF:
    #        key = (grid_x, grid_y)
    #        if key in self.shelf_products and self.shelf_products[key]['quantity'] > 0:
    #            self.shelf_products[key]['quantity'] -= 1
    #            product_type = self.shelf_products[key]['type']
    #            
    #            print(f"Taken {product_type.value} from ({grid_x}, {grid_y}). Remaining: {self.shelf_products[key]['quantity']}")
    #            
    #            # If shelf is empty, we could mark it visually
    #            if self.shelf_products[key]['quantity'] == 0:
    #                print(f"Shelf at ({grid_x}, {grid_y}) is now empty")
    #            
    #            return product_type
    #    return None
    
    def get_shelf_product_type(self, grid_x, grid_y):
        """Get the product type of a shelf."""
        key = (grid_x, grid_y)
        if key in self.shelf_products:
            return self.shelf_products[key]['type']
        return None
    
    def get_shelf_quantity(self, grid_x, grid_y):
        """Get the quantity of products on a shelf."""
        key = (grid_x, grid_y)
        if key in self.shelf_products:
            return self.shelf_products[key]['quantity']
        return 0
    
    def get_nearest_delivery(self, grid_x, grid_y):
        """Get the nearest delivery zone to a position."""
        if not self.delivery_zones:
            return None
            
        nearest = None
        min_distance = float('inf')
        
        for delivery in self.delivery_zones:
            dx = delivery[0] - grid_x
            dy = delivery[1] - grid_y
            distance = dx*dx + dy*dy
            
            if distance < min_distance:
                min_distance = distance
                nearest = delivery
        
        return nearest
    
    def draw(self, screen):
        """Draw the entire warehouse on the screen."""
        # Draw floor and walls first
        self._draw_background(screen)
        
        # Draw shelves with their specific products
        self._draw_shelves(screen)
        
        # Draw delivery zones
        self._draw_delivery_zones(screen)
    
    def _draw_background(self, screen):
        """Draw floor tiles and walls."""
        floor_sprite = self.assets.get("floor")
        wall_left_sprite = self.assets.get("wall_left")
        wall_right_sprite = self.assets.get("wall_right")
        wall_corner_sprite = self.assets.get("wall_corner")
        
        # Draw floor for all cells
        if floor_sprite:
            for row in range(self.height):
                for col in range(self.width):
                    x = self.x_offset + col * self.cell_size
                    y = self.y_offset + row * self.cell_size
                    
                    # Scale floor sprite to cell size
                    scaled_floor = pygame.transform.scale(floor_sprite, 
                                                         (self.cell_size, self.cell_size))
                    screen.blit(scaled_floor, (x, y))
        else:
            # Fallback: draw simple floor
            for row in range(self.height):
                for col in range(self.width):
                    x = self.x_offset + col * self.cell_size
                    y = self.y_offset + row * self.cell_size
                    pygame.draw.rect(screen, (100, 100, 100), (x, y, self.cell_size, self.cell_size))
                    pygame.draw.rect(screen, (80, 80, 80), (x, y, self.cell_size, self.cell_size), 1)
        
        # Draw walls
        if wall_left_sprite and wall_right_sprite and wall_corner_sprite:
            for row in range(self.height):
                for col in range(self.width):
                    if self.grid[row][col] == CellType.WALL:
                        x = self.x_offset + col * self.cell_size
                        y = self.y_offset + row * self.cell_size
                        
                        # Determine wall type based on neighbors
                        is_corner = False
                        if row == 0 and col == 0:
                            sprite = wall_corner_sprite
                            is_corner = True
                        elif row == 0 and col == self.width - 1:
                            sprite = wall_corner_sprite
                            is_corner = True
                        elif row == self.height - 1 and col == 0:
                            sprite = wall_corner_sprite
                            is_corner = True
                        elif row == self.height - 1 and col == self.width - 1:
                            sprite = wall_corner_sprite
                            is_corner = True
                        elif col == 0 or col == self.width - 1:
                            sprite = wall_left_sprite
                        else:
                            sprite = wall_right_sprite
                        
                        if is_corner:
                            # Rotate corner sprites appropriately
                            if row == 0 and col == 0:
                                # Top-left corner
                                pass  # Default orientation
                            elif row == 0 and col == self.width - 1:
                                # Top-right corner
                                sprite = pygame.transform.rotate(sprite, -90)
                            elif row == self.height - 1 and col == 0:
                                # Bottom-left corner
                                sprite = pygame.transform.rotate(sprite, 90)
                            elif row == self.height - 1 and col == self.width - 1:
                                # Bottom-right corner
                                sprite = pygame.transform.rotate(sprite, 180)
                        
                        scaled_wall = pygame.transform.scale(sprite,
                                                           (self.cell_size, self.cell_size))
                        screen.blit(scaled_wall, (x, y))
        else:
            # Fallback: draw simple walls
            for row in range(self.height):
                for col in range(self.width):
                    if self.grid[row][col] == CellType.WALL:
                        x = self.x_offset + col * self.cell_size
                        y = self.y_offset + row * self.cell_size
                        pygame.draw.rect(screen, (50, 50, 50), (x, y, self.cell_size, self.cell_size))
                        pygame.draw.rect(screen, (30, 30, 30), (x, y, self.cell_size, self.cell_size), 2)
    
    def _draw_delivery_zones(self, screen):
        """Draw delivery zones fully filling their own cell (no overlap)."""
        delivery_sprite = self.assets.get("delivery")

        for (col, row) in self.delivery_zones:
            x = self.x_offset + col * self.cell_size
            y = self.y_offset + row * self.cell_size

            if delivery_sprite:
                # Scale delivery sprite to exactly cell size
                scaled_delivery = pygame.transform.scale(delivery_sprite, (self.cell_size, self.cell_size))
                screen.blit(scaled_delivery, (x, y))
                
                # Draw "ENTREGA" text centered
                #font = pygame.font.Font(None, 20)
                #text = font.render("ENTREGA", True, (255, 255, 255))
                #text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                #screen.blit(text, text_rect)
            else:
                # Fallback: simple green square filling the cell
                pygame.draw.rect(screen, (50, 150, 50), (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, (30, 130, 30), (x, y, self.cell_size, self.cell_size), 3)

                # Draw "D" text centered
                font = pygame.font.Font(None, 36)
                text = font.render("D", True, (255, 255, 255))
                text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                screen.blit(text, text_rect)


    
    def _draw_shelves(self, screen):
       """Draw shelves with their specific product sprites AND owners."""

       product_sprites = {
            ProductType.BREAD: self.assets.get("item_bread"),
            ProductType.EGGS: self.assets.get("item_eggs"),
            ProductType.MILK: self.assets.get("item_milk"),
            ProductType.CHOCOLATE: self.assets.get("item_chocolate"),
            ProductType.APPLES: self.assets.get("item_apples"),
            ProductType.TOILET_PAPER: self.assets.get("item_toilet_paper"),
            ProductType.CHIPS: self.assets.get("item_chips"),
        }
       

       name_font = pygame.font.Font(None, 12)

       for (col, row), shelf_info in self.shelf_products.items():
            x = self.x_offset + col * self.cell_size
            y = self.y_offset + row * self.cell_size

            product_type = shelf_info['type']
            quantity = shelf_info['quantity']
            owner = shelf_info.get('owner', 'player')  # safe default

            # ✅ ALWAYS define product_sprite
            product_sprite = product_sprites.get(product_type)

            # Draw shelf
            shelf_sprite = self.assets.get(f"shelf_{product_type.value}")
            if shelf_sprite:
                scaled_shelf = pygame.transform.scale(
                    shelf_sprite, (self.cell_size, self.cell_size)
                )
                screen.blit(scaled_shelf, (x, y))
            else:
                pygame.draw.rect(
                    screen, (120, 80, 40),
                    (x, y, self.cell_size, self.cell_size), 2
                )

                # Draw product image
                product_sprite = product_sprites.get(product_type)
            if product_sprite and quantity > 0:
                item_size = int(self.cell_size * 1.5)
                scaled_item = pygame.transform.scale(product_sprite, (item_size, item_size))
                item_x = x + (self.cell_size - item_size) // 2
                item_y = y + (self.cell_size - item_size) // 2
                screen.blit(scaled_item, (item_x, item_y))

            # 🔴 AI overlay (NOW SAFE)
            #if owner == 'ai':
            #    overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            #    overlay.fill((255, 0, 0, 80))  # red tint
            #    screen.blit(overlay, (x, y))

            # Product name at bottom
            product_name = product_type.value.replace("_", " ").upper()
            name_text = name_font.render(product_name, True, (0, 0, 0))  # black color
            name_rect = name_text.get_rect(
                midbottom=(x + self.cell_size // 2, y + self.cell_size - 2)  # 2 px from bottom
            )
            screen.blit(name_text, name_rect)

            # Quantity at top-right corner
            if quantity > 1:
                qty_font = pygame.font.Font(None, 20)
                qty_text = qty_font.render(str(quantity), True, (255, 0, 0))  # red color
                qty_rect = qty_text.get_rect(
                    topright=(x + self.cell_size - 2, y + 2)  # 2 px padding from top-right
                )
                screen.blit(qty_text, qty_rect)
