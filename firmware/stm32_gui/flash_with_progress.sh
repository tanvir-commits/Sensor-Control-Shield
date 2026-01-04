#!/bin/bash
# Flash firmware with progress bar

BIN_FILE="build/stm32_gui.bin"
ADDRESS="0x08000000"

if [ ! -f "$BIN_FILE" ]; then
    echo "Error: $BIN_FILE not found. Build the project first."
    exit 1
fi

echo "Flashing $BIN_FILE to $ADDRESS..."
echo ""

# Run st-flash and capture output
TEMP_OUTPUT=$(mktemp)
st-flash write "$BIN_FILE" "$ADDRESS" 2>&1 | tee "$TEMP_OUTPUT"

# Parse progress from captured output
TOTAL_PAGES=0
CURRENT_PAGE=0

while IFS= read -r line; do
    # Extract page progress (e.g., "1/49 pages written")
    if [[ $line =~ ([0-9]+)/([0-9]+)[[:space:]]+pages[[:space:]]+written ]]; then
        CURRENT_PAGE="${BASH_REMATCH[1]}"
        TOTAL_PAGES="${BASH_REMATCH[2]}"
        
        if [ "$TOTAL_PAGES" -gt 0 ]; then
            PERCENT=$((CURRENT_PAGE * 100 / TOTAL_PAGES))
            
            # Create progress bar
            BAR_LENGTH=50
            FILLED=$((PERCENT * BAR_LENGTH / 100))
            EMPTY=$((BAR_LENGTH - FILLED))
            
            BAR=$(printf "%*s" $FILLED | tr ' ' '=')
            SPACE=$(printf "%*s" $EMPTY | tr ' ' ' ')
            
            printf "\r[%s%s] %d%% (%d/%d pages)" "$BAR" "$SPACE" "$PERCENT" "$CURRENT_PAGE" "$TOTAL_PAGES"
        fi
    fi
done < "$TEMP_OUTPUT"

rm -f "$TEMP_OUTPUT"

echo ""
echo ""
echo "Resetting board..."
st-flash reset
