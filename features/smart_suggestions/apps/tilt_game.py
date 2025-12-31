"""Tilt Game app - MPU6050 tilt sensor + LCD display."""

import time
from typing import Optional
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo


class TiltGameApp(BaseApp):
    """Tilt game - move a ball on LCD by tilting MPU6050."""
    
    def __init__(self):
        super().__init__()
        self.update_interval = 33  # ~30 Hz for smooth animation
        self.mpu6050_device: Optional[DeviceInfo] = None
        self.lcd_device: Optional[DeviceInfo] = None
        self.mpu6050 = None
        self.display = None
        
        # Ball physics
        self.ball_x = 64  # Center of 128x64 display
        self.ball_y = 32
        self.ball_radius = 3
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.friction = 0.95  # Friction coefficient
        self.sensitivity = 3.0  # Tilt sensitivity (increased for better response)
        self.debug = False  # Set to True for debug output
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("TiltGameApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("TiltGameApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("TiltGameApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("TiltGameApp: Failed to initialize LCD")
                return False
            
            # Clear display and draw initial ball
            self._draw_ball()
            
            return True
        
        except Exception as e:
            print(f"TiltGameApp initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_mpu6050(self) -> bool:
        """Initialize MPU6050 sensor."""
        try:
            # Try to use adafruit-circuitpython-mpu6050
            try:
                import board
                import adafruit_mpu6050
                
                i2c = board.I2C()
                self.mpu6050 = adafruit_mpu6050.MPU6050(i2c)
                return True
            
            except ImportError:
                # Fallback: Try mpu6050-raspberrypi
                try:
                    from mpu6050 import mpu6050
                    self.mpu6050 = mpu6050(0x68)  # Default address
                    return True
                
                except ImportError:
                    # Fallback: Direct I2C access (basic implementation)
                    print("TiltGameApp: Using basic I2C MPU6050 access")
                    return self._init_mpu6050_basic()
        
        except Exception as e:
            print(f"TiltGameApp: MPU6050 init error: {e}")
            return False
    
    def _init_mpu6050_basic(self) -> bool:
        """Basic MPU6050 initialization via direct I2C."""
        try:
            import smbus2
            self.mpu6050_bus = smbus2.SMBus(self.mpu6050_device.bus)
            self.mpu6050_addr = self.mpu6050_device.address
            
            # Wake up MPU6050 (set PWR_MGMT_1 register to 0)
            self.mpu6050_bus.write_byte_data(self.mpu6050_addr, 0x6B, 0)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"TiltGameApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_accel(self) -> tuple:
        """Read accelerometer data from MPU6050.
        
        Returns:
            (x, y, z) accelerometer values in m/s^2
        """
        try:
            if hasattr(self.mpu6050, 'acceleration'):
                # adafruit library
                accel = self.mpu6050.acceleration
                return (accel[0], accel[1], accel[2])
            
            elif hasattr(self.mpu6050, 'get_accel_data'):
                # mpu6050-raspberrypi library
                accel = self.mpu6050.get_accel_data()
                return (accel['x'], accel['y'], accel['z'])
            
            else:
                # Basic I2C read
                return self._read_mpu6050_accel_basic()
        
        except Exception as e:
            print(f"TiltGameApp: Error reading MPU6050: {e}")
            return (0.0, 0.0, 9.8)  # Default: no tilt
    
    def _read_mpu6050_accel_basic(self) -> tuple:
        """Basic I2C accelerometer read."""
        try:
            # MPU6050 accelerometer registers start at 0x3B
            # Each axis is 2 bytes (high, low)
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x3B, 6)
            
            # Convert to signed integers
            accel_x = (data[0] << 8 | data[1])
            if accel_x > 32767:
                accel_x -= 65536
            accel_x = accel_x / 16384.0  # Convert to g (FS_SEL=0, ±2g)
            
            accel_y = (data[2] << 8 | data[3])
            if accel_y > 32767:
                accel_y -= 65536
            accel_y = accel_y / 16384.0
            
            accel_z = (data[4] << 8 | data[5])
            if accel_z > 32767:
                accel_z -= 65536
            accel_z = accel_z / 16384.0
            
            return (accel_x, accel_y, accel_z)
        
        except Exception as e:
            print(f"TiltGameApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 9.8)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display."""
        try:
            import board
            import adafruit_ssd1306
            from PIL import Image, ImageDraw
            
            i2c = board.I2C()
            
            # Try 128x64 first, fallback to 128x32
            try:
                self.display = adafruit_ssd1306.SSD1306_I2C(
                    128, 64, i2c, addr=self.lcd_device.address
                )
                self.display_width = 128
                self.display_height = 64
            except:
                self.display = adafruit_ssd1306.SSD1306_I2C(
                    128, 32, i2c, addr=self.lcd_device.address
                )
                self.display_width = 128
                self.display_height = 32
                self.ball_y = 16  # Adjust for smaller display
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            return True
        
        except Exception as e:
            print(f"TiltGameApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update game loop - read tilt and move ball."""
        if not self.running:
            return
        
        try:
            # Read accelerometer
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            
            # Calculate tilt from accelerometer
            # MPU6050 returns values in "g" (gravity units)
            # When flat: X≈0, Y≈0, Z≈1g
            # When tilted: X and Y show tilt angle
            # Apply sensitivity and invert Y for natural feel
            tilt_x = accel_x * self.sensitivity
            tilt_y = -accel_y * self.sensitivity  # Invert for natural feel
            
            # Debug output (first few frames only)
            if self.debug and hasattr(self, '_debug_count'):
                self._debug_count += 1
                if self._debug_count < 10:
                    print(f"TiltGame: accel=({accel_x:.3f}, {accel_y:.3f}, {accel_z:.3f}) tilt=({tilt_x:.3f}, {tilt_y:.3f})")
            elif self.debug and not hasattr(self, '_debug_count'):
                self._debug_count = 0
            
            # Add small dead zone to prevent drift when flat
            if abs(tilt_x) < 0.1:
                tilt_x = 0.0
            if abs(tilt_y) < 0.1:
                tilt_y = 0.0
            
            # Update velocity based on tilt
            self.velocity_x += tilt_x
            self.velocity_y += tilt_y
            
            # Apply friction
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
            
            # Update ball position
            self.ball_x += self.velocity_x
            self.ball_y += self.velocity_y
            
            # Bounce off walls
            if self.ball_x < self.ball_radius:
                self.ball_x = self.ball_radius
                self.velocity_x *= -0.8  # Bounce with damping
            elif self.ball_x > self.display_width - self.ball_radius:
                self.ball_x = self.display_width - self.ball_radius
                self.velocity_x *= -0.8
            
            if self.ball_y < self.ball_radius:
                self.ball_y = self.ball_radius
                self.velocity_y *= -0.8
            elif self.ball_y > self.display_height - self.ball_radius:
                self.ball_y = self.display_height - self.ball_radius
                self.velocity_y *= -0.8
            
            # Draw ball
            self._draw_ball()
        
        except Exception as e:
            print(f"TiltGameApp update error: {e}")
    
    def _draw_ball(self) -> None:
        """Draw ball on LCD display."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Draw ball (filled circle)
            self.draw.ellipse(
                (
                    int(self.ball_x - self.ball_radius),
                    int(self.ball_y - self.ball_radius),
                    int(self.ball_x + self.ball_radius),
                    int(self.ball_y + self.ball_radius)
                ),
                fill=1
            )
            
            # Update display
            self.display.image(self.image)
            self.display.show()
        
        except Exception as e:
            print(f"TiltGameApp draw error: {e}")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            # Clear display
            if self.display:
                self.display.fill(0)
                self.display.show()
            
            # Close I2C bus if using basic access
            if hasattr(self, 'mpu6050_bus'):
                try:
                    self.mpu6050_bus.close()
                except:
                    pass
        
        except Exception as e:
            print(f"TiltGameApp cleanup error: {e}")

