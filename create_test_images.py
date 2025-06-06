#!/usr/bin/env python3
"""
Create test images for Solar AI Platform
This script generates realistic satellite roof images for testing
"""

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image_1():
    """Create a simple rectangular roof image"""
    # Create a 800x600 image
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Add sky background (light blue)
    img[:, :] = [135, 206, 235]  # Sky blue
    
    # Add ground/grass (green)
    img[400:, :] = [34, 139, 34]  # Forest green
    
    # Add main house roof (dark gray)
    roof_points = np.array([[200, 200], [600, 200], [650, 350], [150, 350]], np.int32)
    cv2.fillPoly(img, [roof_points], (70, 70, 70))
    
    # Add roof ridge line
    cv2.line(img, (200, 200), (600, 200), (50, 50, 50), 3)
    
    # Add some texture to roof
    for i in range(220, 340, 20):
        cv2.line(img, (180, i), (620, i), (60, 60, 60), 1)
    
    # Add chimney
    cv2.rectangle(img, (450, 150), (480, 200), (139, 69, 19), -1)
    
    # Add some trees for shading simulation
    cv2.circle(img, (100, 300), 50, (0, 100, 0), -1)
    cv2.circle(img, (700, 320), 40, (0, 100, 0), -1)
    
    return img

def create_test_image_2():
    """Create a complex multi-section roof"""
    # Create a 1000x800 image
    img = np.zeros((800, 1000, 3), dtype=np.uint8)
    
    # Add sky background
    img[:, :] = [135, 206, 235]
    
    # Add ground
    img[600:, :] = [34, 139, 34]
    
    # Main roof section (L-shaped)
    main_roof = np.array([[150, 250], [500, 250], [500, 400], [350, 400], [350, 500], [150, 500]], np.int32)
    cv2.fillPoly(img, [main_roof], (80, 80, 80))
    
    # Secondary roof section
    sec_roof = np.array([[500, 250], [750, 250], [750, 450], [500, 450]], np.int32)
    cv2.fillPoly(img, [sec_roof], (90, 90, 90))
    
    # Add roof lines and texture
    cv2.line(img, (150, 250), (500, 250), (60, 60, 60), 2)
    cv2.line(img, (500, 250), (750, 250), (60, 60, 60), 2)
    
    # Add solar panels on one section
    panel_color = (25, 25, 112)  # Dark blue for solar panels
    for x in range(520, 720, 40):
        for y in range(270, 420, 30):
            cv2.rectangle(img, (x, y), (x+35, y+25), panel_color, -1)
            cv2.rectangle(img, (x, y), (x+35, y+25), (0, 0, 0), 1)
    
    # Add some obstacles (HVAC units)
    cv2.rectangle(img, (200, 300), (250, 350), (160, 160, 160), -1)
    cv2.rectangle(img, (300, 320), (340, 360), (160, 160, 160), -1)
    
    return img

def create_test_image_3():
    """Create a residential house with angled roof"""
    # Create a 900x700 image
    img = np.zeros((700, 900, 3), dtype=np.uint8)
    
    # Sky background with some clouds
    img[:, :] = [135, 206, 235]
    
    # Add some cloud effects
    cv2.ellipse(img, (200, 100), (80, 40), 0, 0, 360, (255, 255, 255), -1)
    cv2.ellipse(img, (600, 80), (60, 30), 0, 0, 360, (255, 255, 255), -1)
    
    # Ground
    img[500:, :] = [34, 139, 34]
    
    # House walls
    cv2.rectangle(img, (250, 350), (650, 500), (222, 184, 135), -1)
    
    # Triangular roof
    roof_triangle = np.array([[200, 350], [450, 200], [700, 350]], np.int32)
    cv2.fillPoly(img, [roof_triangle], (139, 69, 19))  # Brown roof
    
    # Add roof shingles texture
    for y in range(220, 350, 15):
        for x in range(220 + (y-220)//3, 680 - (y-220)//3, 30):
            cv2.line(img, (x, y), (x+20, y), (120, 60, 15), 2)
    
    # Add gutters
    cv2.line(img, (200, 350), (700, 350), (100, 100, 100), 3)
    
    # Add dormer window
    dormer_points = np.array([[380, 280], [420, 250], [460, 280], [460, 320], [380, 320]], np.int32)
    cv2.fillPoly(img, [dormer_points], (139, 69, 19))
    cv2.rectangle(img, (390, 290), (450, 315), (173, 216, 230), -1)  # Window
    
    # Add some landscaping
    cv2.circle(img, (150, 450), 60, (0, 100, 0), -1)  # Tree
    cv2.circle(img, (750, 480), 45, (0, 100, 0), -1)  # Tree
    
    return img

def create_test_image_4():
    """Create a commercial building with flat roof"""
    # Create a 1200x800 image
    img = np.zeros((800, 1200, 3), dtype=np.uint8)
    
    # Sky
    img[:, :] = [135, 206, 235]
    
    # Ground
    img[600:, :] = [105, 105, 105]  # Concrete/asphalt
    
    # Large flat roof building
    cv2.rectangle(img, (200, 200), (1000, 600), (128, 128, 128), -1)
    
    # Roof membrane texture
    for x in range(220, 980, 40):
        cv2.line(img, (x, 220), (x, 580), (110, 110, 110), 1)
    for y in range(220, 580, 30):
        cv2.line(img, (220, y), (980, y), (110, 110, 110), 1)
    
    # HVAC units
    cv2.rectangle(img, (300, 250), (400, 350), (160, 160, 160), -1)
    cv2.rectangle(img, (500, 280), (580, 360), (160, 160, 160), -1)
    cv2.rectangle(img, (700, 240), (800, 340), (160, 160, 160), -1)
    
    # Existing solar array
    panel_color = (25, 25, 112)
    for x in range(250, 450, 35):
        for y in range(400, 550, 25):
            cv2.rectangle(img, (x, y), (x+30, y+20), panel_color, -1)
            cv2.rectangle(img, (x, y), (x+30, y+20), (0, 0, 0), 1)
    
    # Roof access and utilities
    cv2.rectangle(img, (850, 300), (900, 350), (139, 69, 19), -1)  # Roof access
    cv2.circle(img, (920, 280), 15, (255, 255, 0), -1)  # Vent
    
    return img

def save_images():
    """Save all test images"""
    # Create test_images directory if it doesn't exist
    os.makedirs('test_images', exist_ok=True)
    
    # Create and save images
    images = [
        (create_test_image_1(), 'residential_simple_roof.jpg', 'Simple rectangular residential roof'),
        (create_test_image_2(), 'complex_multi_section_roof.jpg', 'Complex L-shaped roof with existing panels'),
        (create_test_image_3(), 'angled_residential_roof.jpg', 'Traditional angled residential roof'),
        (create_test_image_4(), 'commercial_flat_roof.jpg', 'Commercial flat roof with HVAC units')
    ]
    
    print("🖼️  Creating test images for Solar AI Platform...")
    print("=" * 50)
    
    for img_array, filename, description in images:
        # Convert BGR to RGB for PIL
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(img_rgb)
        
        # Add metadata text
        draw = ImageDraw.Draw(pil_img)
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add description text
        text_color = (255, 255, 255)
        text_bg_color = (0, 0, 0)
        text = f"Test Image: {description}"
        
        # Add text background
        if font:
            bbox = draw.textbbox((10, 10), text, font=font)
            draw.rectangle(bbox, fill=text_bg_color)
            draw.text((10, 10), text, fill=text_color, font=font)
        
        # Save image
        filepath = os.path.join('test_images', filename)
        pil_img.save(filepath, 'JPEG', quality=95)
        
        print(f"✅ Created: {filename}")
        print(f"   Description: {description}")
        print(f"   Size: {pil_img.size}")
        print(f"   Path: {filepath}")
        print()
    
    print("🎉 All test images created successfully!")
    print("\n📝 Usage Instructions:")
    print("1. Navigate to the test_images folder")
    print("2. Upload any of these images to the Solar AI Platform")
    print("3. Use these sample coordinates for testing:")
    print("   - Residential: Latitude 37.7749, Longitude -122.4194 (San Francisco)")
    print("   - Commercial: Latitude 40.7128, Longitude -74.0060 (New York)")
    print("4. Try different electricity rates: $0.10-0.30 per kWh")
    print("5. Test various installation costs: $2.50-4.00 per watt")

if __name__ == "__main__":
    save_images()
