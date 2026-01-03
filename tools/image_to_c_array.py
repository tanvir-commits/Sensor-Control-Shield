#!/usr/bin/env python3
"""
Convert PNG/JPG images to RGB565 C array format for STM32 LCD displays.
Output format matches Waveshare reference code pattern.
"""

import sys
import argparse
from PIL import Image
import os

def rgb_to_rgb565(r, g, b):
    """Convert 8-bit RGB to 16-bit RGB565 format."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_c_array(image_path, output_c, output_h, array_name, resize=None):
    """
    Convert image to RGB565 C array.
    
    Args:
        image_path: Path to input image (PNG/JPG)
        output_c: Path to output .c file
        output_h: Path to output .h file
        array_name: Name for the C array (e.g., 'gImage_delivery_screen')
        resize: Optional tuple (width, height) to resize image
    """
    # Load and convert image
    img = Image.open(image_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if requested
    if resize:
        img = img.resize(resize, Image.Resampling.LANCZOS)
    
    width, height = img.size
    pixels = img.load()
    
    # Generate array name
    var_name = array_name
    size_name = f"{array_name}_size"
    
    # Calculate total size (2 bytes per pixel)
    total_bytes = width * height * 2
    
    # Generate .c file
    with open(output_c, 'w') as f:
        f.write(f"// Auto-generated from {os.path.basename(image_path)}\n")
        f.write(f"// Size: {width}x{height} pixels ({total_bytes} bytes)\n")
        f.write(f"// Format: RGB565 (little-endian byte order)\n\n")
        f.write(f"#include \"{os.path.basename(output_h)}\"\n\n")
        f.write(f"const unsigned char {var_name}[{total_bytes}] = {{\n")
        
        # Write pixel data in row-major order, little-endian format
        # Format: LSB first, MSB second (matching reference code)
        bytes_written = 0
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                rgb565 = rgb_to_rgb565(r, g, b)
                
                # Little-endian: LSB first, MSB second
                lsb = rgb565 & 0xFF
                msb = (rgb565 >> 8) & 0xFF
                
                # Add comma except for last pixel
                if y == height - 1 and x == width - 1:
                    f.write(f"0x{lsb:02X},0x{msb:02X}")
                else:
                    f.write(f"0x{lsb:02X},0x{msb:02X},")
                bytes_written += 2
                
                # Newline every 16 bytes (8 pixels) for readability
                if bytes_written % 16 == 0:
                    f.write("\n")
        
        f.write(f"\n}};\n\n")
        f.write(f"const uint32_t {size_name} = {total_bytes};\n")
    
    # Generate .h file
    with open(output_h, 'w') as f:
        # Generate unique header guard from filename
        header_guard_base = os.path.basename(output_h).upper().replace('.', '_')
        header_guard = header_guard_base
        f.write(f"#ifndef {header_guard}\n")
        f.write(f"#define {header_guard}\n\n")
        f.write(f"#include <stdint.h>\n\n")
        f.write(f"// Auto-generated from {os.path.basename(image_path)}\n")
        f.write(f"// Size: {width}x{height} pixels\n\n")
        f.write(f"extern const unsigned char {var_name}[];\n")
        f.write(f"extern const uint32_t {size_name};\n\n")
        f.write(f"#define {array_name.upper()}_WIDTH  {width}\n")
        f.write(f"#define {array_name.upper()}_HEIGHT {height}\n\n")
        f.write(f"#endif // {header_guard}\n")
    
    print(f"✓ Converted {image_path} ({width}x{height}) to {output_c}")
    print(f"  Array: {var_name}[{total_bytes} bytes]")
    return width, height, total_bytes

def main():
    parser = argparse.ArgumentParser(
        description='Convert images to RGB565 C arrays for STM32 LCD'
    )
    parser.add_argument('input', help='Input image file (PNG/JPG)')
    parser.add_argument('-o', '--output', help='Output base name (without extension)')
    parser.add_argument('-n', '--name', help='C array name (default: gImage_<filename>)')
    parser.add_argument('-r', '--resize', help='Resize to WxH (e.g., 320x240)', metavar='WxH')
    parser.add_argument('--c-file', help='Output .c file path')
    parser.add_argument('--h-file', help='Output .h file path')
    
    args = parser.parse_args()
    
    # Determine output names
    if args.output:
        base_name = args.output
    else:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
    
    if args.name:
        array_name = args.name
    else:
        array_name = f"gImage_{base_name}"
    
    if args.c_file:
        output_c = args.c_file
    else:
        output_c = f"{base_name}.c"
    
    if args.h_file:
        output_h = args.h_file
    else:
        output_h = f"{base_name}.h"
    
    # Parse resize
    resize = None
    if args.resize:
        w, h = map(int, args.resize.split('x'))
        resize = (w, h)
    
    # Convert
    try:
        image_to_c_array(args.input, output_c, output_h, array_name, resize)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

