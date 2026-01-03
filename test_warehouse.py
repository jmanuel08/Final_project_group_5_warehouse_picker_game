"""
Test script for warehouse generation
"""

import pygame
import sys
import traceback
from src.asset_loader import AssetLoader
from src.warehouse import Warehouse, ProductType

print("Testing warehouse generation...")

# Initialize pygame display for testing
pygame.init()
# Create a minimal display (1x1 pixel) to allow image conversion
pygame.display.set_mode((1, 1), pygame.HIDDEN)

try:
    # Load assets
    print("Loading assets...")
    asset_loader = AssetLoader()
    asset_loader.load_all()
    
    # Try to create warehouse
    print("Creating warehouse...")
    warehouse = Warehouse(
        x_offset=50,
        y_offset=100,
        width=10,
        height=10,
        cell_size=64,
        asset_loader=asset_loader,
        level=1,
        required_products=[ProductType.BREAD, ProductType.EGGS]
    )
    
    print("SUCCESS: Warehouse created!")
    print(f"  Delivery zones: {warehouse.delivery_zones}")
    print(f"  Shelf count: {len(warehouse.shelf_products)}")
    print(f"  Grid size: {warehouse.width}x{warehouse.height}")
    
    # Print shelf positions
    for (x, y), info in warehouse.shelf_products.items():
        print(f"  Shelf at ({x}, {y}): {info['type'].value}, qty: {info['quantity']}")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
finally:
    pygame.quit()