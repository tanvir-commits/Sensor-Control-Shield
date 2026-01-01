"""Spinning Gyroscope app - MPU6050 + LCD display.

Shows a large spinning disc/ring that responds to rotation.
Perfect for desk demos - rotate device slightly to see gyroscope spin.
"""

import math
from typing import Optional, List, Tuple
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo
from ..display.display_factory import DisplayFactory
from ..display.display_interface import DisplayInterface


class SpinningGyroscopeApp(BaseApp):
    """Spinning Gyroscope - large spinning disc that responds to rotation."""
    
    def __init__(self):
        super().__init__()
        self.update_interval = 33  # ~30 Hz for smooth animation
        self.mpu6050_device: Optional[DeviceInfo] = None
        self.lcd_device: Optional[DeviceInfo] = None
        self.mpu6050 = None
        self.display: Optional[DisplayInterface] = None
        
        # Display dimensions (will be set from display)
        self.display_width = 128
        self.display_height = 64
        self.center_x = 64
        self.center_y = 32
        
        # Gyroscope rotation
        self.rotation_angle = 0.0  # Current rotation angle in radians
        self.rotation_speed = 0.0  # Rotation speed in radians per frame
        self.max_rotation_speed = 0.3  # Maximum rotation speed
        self.friction = 0.98  # Friction coefficient (slows down over time)
        
        # Gyroscope size
        self.gyro_radius = 25
        self.gyro_thickness = 3
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("SpinningGyroscopeApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("SpinningGyroscopeApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("SpinningGyroscopeApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("SpinningGyroscopeApp: Failed to initialize LCD")
                return False
            
            # Draw initial gyroscope
            self._draw_gyroscope()
            
            return True
        
        except Exception as e:
            print(f"SpinningGyroscopeApp initialization error: {e}")
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
                    self.mpu6050 = mpu6050(0x68)
                    return True
                
                except ImportError:
                    # Fallback: Direct I2C access
                    return self._init_mpu6050_basic()
        
        except Exception as e:
            print(f"SpinningGyroscopeApp: MPU6050 init error: {e}")
            return False
    
    def _init_mpu6050_basic(self) -> bool:
        """Basic MPU6050 initialization via direct I2C."""
        try:
            import smbus2
            import time
            self.mpu6050_bus = smbus2.SMBus(self.mpu6050_device.bus)
            self.mpu6050_addr = self.mpu6050_device.address
            
            # Wake up MPU6050
            self.mpu6050_bus.write_byte_data(self.mpu6050_addr, 0x6B, 0)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"SpinningGyroscopeApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_gyro(self) -> tuple:
        """Read gyroscope data from MPU6050.
        
        Returns:
            (x, y, z) gyroscope values in degrees/second
        """
        try:
            if hasattr(self.mpu6050, 'gyro'):
                # adafruit library
                gyro = self.mpu6050.gyro
                return (gyro[0], gyro[1], gyro[2])
            
            elif hasattr(self.mpu6050, 'get_gyro_data'):
                # mpu6050-raspberrypi library
                gyro = self.mpu6050.get_gyro_data()
                return (gyro['x'], gyro['y'], gyro['z'])
            
            else:
                # Basic I2C read
                return self._read_mpu6050_gyro_basic()
        
        except Exception as e:
            print(f"SpinningGyroscopeApp: Error reading gyro: {e}")
            return (0.0, 0.0, 0.0)
    
    def _read_mpu6050_gyro_basic(self) -> tuple:
        """Basic I2C gyroscope read."""
        try:
            # MPU6050 gyroscope registers start at 0x43
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x43, 6)
            
            # Convert to signed integers
            gyro_x = (data[0] << 8 | data[1])
            if gyro_x > 32767:
                gyro_x -= 65536
            gyro_x = gyro_x / 131.0  # Convert to degrees/sec (FS_SEL=0, ±250°/s)
            
            gyro_y = (data[2] << 8 | data[3])
            if gyro_y > 32767:
                gyro_y -= 65536
            gyro_y = gyro_y / 131.0
            
            gyro_z = (data[4] << 8 | data[5])
            if gyro_z > 32767:
                gyro_z -= 65536
            gyro_z = gyro_z / 131.0
            
            return (gyro_x, gyro_y, gyro_z)
        
        except Exception as e:
            print(f"SpinningGyroscopeApp: Basic gyro read error: {e}")
            return (0.0, 0.0, 0.0)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display using display abstraction layer."""
        try:
            from PIL import Image, ImageDraw
            
            self.display = DisplayFactory.create_display(self.lcd_device)
            if not self.display:
                print("SpinningGyroscopeApp: Failed to create display adapter")
                return False
            
            self.display_width, self.display_height = self.display.get_size()
            self.center_x = self.display_width // 2
            self.center_y = self.display_height // 2
            
            # Adjust gyroscope size based on display
            self.gyro_radius = min(self.display_width, self.display_height) // 3
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            self.display.clear()
            return True
        
        except Exception as e:
            print(f"SpinningGyroscopeApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update gyroscope rotation."""
        if not self.running:
            return
        
        try:
            # Read gyroscope (Z-axis rotation)
            gyro_x, gyro_y, gyro_z = self._read_mpu6050_gyro()
            
            # Use Z-axis rotation (rotation around vertical axis)
            # Convert degrees/sec to radians per frame
            # Scale down for smoother control
            gyro_z_rad_per_frame = math.radians(gyro_z) * 0.05
            
            # Update rotation speed based on gyroscope
            # Add to existing speed (accumulate)
            self.rotation_speed += gyro_z_rad_per_frame
            
            # Limit maximum speed
            if abs(self.rotation_speed) > self.max_rotation_speed:
                self.rotation_speed = self.max_rotation_speed if self.rotation_speed > 0 else -self.max_rotation_speed
            
            # Apply friction (slow down over time)
            self.rotation_speed *= self.friction
            
            # Update rotation angle
            self.rotation_angle += self.rotation_speed
            
            # Keep angle in [0, 2π] range
            self.rotation_angle = self.rotation_angle % (2 * math.pi)
            
            # Draw gyroscope
            self._draw_gyroscope()
        
        except Exception as e:
            print(f"SpinningGyroscopeApp update error: {e}")
    
    def _draw_gyroscope(self) -> None:
        """Draw spinning gyroscope disc."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Draw outer ring
            outer_radius = self.gyro_radius
            inner_radius = self.gyro_radius - self.gyro_thickness
            
            # Draw main disc (filled circle)
            self.draw.ellipse(
                (
                    self.center_x - outer_radius,
                    self.center_y - outer_radius,
                    self.center_x + outer_radius,
                    self.center_y + outer_radius
                ),
                outline=1,
                width=2
            )
            
            # Draw inner circle
            self.draw.ellipse(
                (
                    self.center_x - inner_radius,
                    self.center_y - inner_radius,
                    self.center_x + inner_radius,
                    self.center_y + inner_radius
                ),
                outline=1,
                width=1
            )
            
            # Draw spokes (8 spokes for visual effect)
            num_spokes = 8
            for i in range(num_spokes):
                angle = self.rotation_angle + (i * 2 * math.pi / num_spokes)
                start_x = self.center_x + inner_radius * 0.3 * math.cos(angle)
                start_y = self.center_y + inner_radius * 0.3 * math.sin(angle)
                end_x = self.center_x + inner_radius * 0.9 * math.cos(angle)
                end_y = self.center_y + inner_radius * 0.9 * math.sin(angle)
                
                self.draw.line(
                    (int(start_x), int(start_y), int(end_x), int(end_y)),
                    fill=1,
                    width=1
                )
            
            # Draw center dot
            center_size = 2
            self.draw.ellipse(
                (
                    self.center_x - center_size,
                    self.center_y - center_size,
                    self.center_x + center_size,
                    self.center_y + center_size
                ),
                fill=1
            )
            
            # Draw rotation indicator (arrow)
            arrow_length = self.gyro_radius - 5
            arrow_x = self.center_x + arrow_length * math.cos(self.rotation_angle)
            arrow_y = self.center_y + arrow_length * math.sin(self.rotation_angle)
            
            # Draw arrow line
            self.draw.line(
                (self.center_x, self.center_y, int(arrow_x), int(arrow_y)),
                fill=1,
                width=2
            )
            
            # Draw arrowhead
            arrow_angle1 = self.rotation_angle + math.pi - 0.3
            arrow_angle2 = self.rotation_angle + math.pi + 0.3
            arrow_size = 4
            
            arrow1_x = arrow_x + arrow_size * math.cos(arrow_angle1)
            arrow1_y = arrow_y + arrow_size * math.sin(arrow_angle1)
            arrow2_x = arrow_x + arrow_size * math.cos(arrow_angle2)
            arrow2_y = arrow_y + arrow_size * math.sin(arrow_angle2)
            
            self.draw.polygon(
                [
                    (int(arrow_x), int(arrow_y)),
                    (int(arrow1_x), int(arrow1_y)),
                    (int(arrow2_x), int(arrow2_y))
                ],
                fill=1
            )
            
            # Draw speed indicator (text or bar)
            speed_percent = abs(self.rotation_speed) / self.max_rotation_speed * 100
            speed_text = f"{speed_percent:.0f}%"
            
            # Draw speed bar
            bar_width = 40
            bar_height = 4
            bar_x = self.center_x - bar_width // 2
            bar_y = self.display_height - 10
            
            # Background bar
            self.draw.rectangle(
                (bar_x, bar_y, bar_x + bar_width, bar_y + bar_height),
                outline=1,
                width=1
            )
            
            # Filled portion
            fill_width = int(bar_width * (abs(self.rotation_speed) / self.max_rotation_speed))
            if fill_width > 0:
                self.draw.rectangle(
                    (bar_x, bar_y, bar_x + fill_width, bar_y + bar_height),
                    fill=1
                )
            
            # Update display
            self.display.show_image(self.image)
        
        except Exception as e:
            print(f"SpinningGyroscopeApp draw error: {e}")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.display:
                self.display.clear()
                self.display.cleanup()
                self.display = None
            
            if hasattr(self, 'mpu6050_bus'):
                try:
                    self.mpu6050_bus.close()
                except:
                    pass
        
        except Exception as e:
            print(f"SpinningGyroscopeApp cleanup error: {e}")


