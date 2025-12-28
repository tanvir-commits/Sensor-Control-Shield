"""Pin configuration for Raspberry Pi."""

# LED pins
LED1 = 16  # BCM16
LED2 = 17  # BCM17
LED3 = 27  # BCM27
LED4 = 22  # BCM22

# Button pins
BTN1 = 23  # BCM23
BTN2 = 24  # BCM24

# Sensor power control
SENSOR_POWER = 26  # BCM26

# I2C bus
# Set to None to auto-detect, or specify bus number (1 for Pi 4, 13/14 for Pi 5)
I2C_BUS = None  # Auto-detect

# ADC I2C address
ADC_ADDRESS = 0x48  # ADS1115 default address


