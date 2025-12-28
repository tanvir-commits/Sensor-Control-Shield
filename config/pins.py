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
# Set to None to auto-detect, or specify bus number
# - Bus 1: I2C1 (GPIO2/GPIO3, pins 3/5) - Default, used by ADC and J12/J13
# - Bus 3: I2C3 (GPIO4/GPIO5, pins 7/29) - Requires dtoverlay=i2c3,pins_4_5, used by J16
# - Bus 13/14: I2C6/I2C7 on Pi 5 (native buses)
I2C_BUS = None  # Auto-detect

# I2C3 bus (second I2C bus on GPIO4/GPIO5)
# Used by J16 (I2C_PORT_C)
I2C3_BUS = 3  # I2C3 bus number

# ADC I2C address
ADC_ADDRESS = 0x48  # ADS1115 default address


