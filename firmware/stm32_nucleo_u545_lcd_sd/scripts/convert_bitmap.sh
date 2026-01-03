#!/bin/bash
# Simple script to convert PNG/JPG images to C arrays for STM32 LCD
# Usage: ./convert_bitmap.sh <image_file> [output_name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOL_PATH="$PROJECT_ROOT/../../tools/image_to_c_array.py"
IMAGES_DIR="$PROJECT_ROOT/images"
SRC_DIR="$PROJECT_ROOT/src"
INC_DIR="$PROJECT_ROOT/inc"

# Check if image file provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <image_file> [output_name]"
    echo ""
    echo "Examples:"
    echo "  $0 my_image.png"
    echo "  $0 my_image.png my_bitmap"
    echo ""
    echo "Output files will be created in:"
    echo "  - C source: $SRC_DIR/gui_images_<name>.c"
    echo "  - Header:   $INC_DIR/gui_images_<name>.h"
    exit 1
fi

IMAGE_FILE="$1"
OUTPUT_NAME="$2"

# Check if image file exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo "Error: Image file not found: $IMAGE_FILE"
    exit 1
fi

# Determine output name
if [ -z "$OUTPUT_NAME" ]; then
    # Use image filename without extension
    OUTPUT_NAME=$(basename "$IMAGE_FILE" | sed 's/\.[^.]*$//')
fi

# Generate array name (convert to valid C identifier)
ARRAY_NAME="gImage_${OUTPUT_NAME}"
ARRAY_NAME=$(echo "$ARRAY_NAME" | sed 's/[^a-zA-Z0-9_]/_/g')

# Output file paths
OUTPUT_C="$SRC_DIR/gui_images_${OUTPUT_NAME}.c"
OUTPUT_H="$INC_DIR/gui_images_${OUTPUT_NAME}.h"

# Check if tool exists
if [ ! -f "$TOOL_PATH" ]; then
    echo "Error: Image conversion tool not found: $TOOL_PATH"
    exit 1
fi

# Resize to LCD dimensions (240x320 portrait mode)
# Display is 240 pixels wide x 320 pixels tall in portrait orientation
LCD_WIDTH=240
LCD_HEIGHT=320

echo "Converting image: $IMAGE_FILE"
echo "Output name: $OUTPUT_NAME"
echo "Array name: $ARRAY_NAME"
echo "Resize to: ${LCD_WIDTH}x${LCD_HEIGHT}"
echo ""

# Run conversion tool
python3 "$TOOL_PATH" "$IMAGE_FILE" \
    --name "$ARRAY_NAME" \
    --resize "${LCD_WIDTH}x${LCD_HEIGHT}" \
    --c-file "$OUTPUT_C" \
    --h-file "$OUTPUT_H"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Success! Files created:"
    echo "  - $OUTPUT_C"
    echo "  - $OUTPUT_H"
    echo ""
    echo "Next steps:"
    echo "1. Add to Makefile: src/gui_images_${OUTPUT_NAME}.c"
    echo "2. Include in gui_images.h: #include \"gui_images_${OUTPUT_NAME}.h\""
    echo "3. Register in code: BitmapGUI_RegisterBitmap(gImage_${OUTPUT_NAME}, ...)"
else
    echo "Error: Conversion failed"
    exit 1
fi

