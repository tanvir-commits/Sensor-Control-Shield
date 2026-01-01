"""Motion Trail app - MPU6050 + LCD display.

Shows a ball/dot that leaves a fading trail creating patterns.
Perfect for desk demos - tilt device to draw patterns.
"""

import math
from typing import Optional, List, Tuple
from collections import deque
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo
from ..display.display_factory import DisplayFactory
from ..display.display_interface import DisplayInterface


class TrailPoint:
    """A point in the motion trail."""
    
    def __init__(self, x: float, y: float, brightness: float = 1.0):
        self.x = x
        self.y = y
        self.brightness = brightness  # 1.0 = full, 0.0 = invisible
        self.age = 0  # Age in frames
    
    def update(self, fade_rate: float = 0.05):
        """Update trail point (fade out)."""
        self.brightness -= fade_rate
        if self.brightness < 0:
            self.brightness = 0
        self.age += 1


class MotionTrailApp(BaseApp):
    """Motion Trail - ball that leaves a fading trail."""
    
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
        
        # Ball position and movement
        self.ball_x = 64.0
        self.ball_y = 32.0
        self.ball_radius = 3
        
        # Movement parameters - constant speed based on tilt (no acceleration)
        self.speed_factor = 6.0  # Speed multiplier - increased for much better responsiveness
        self.center_x = 64.0  # Will be set from display
        self.center_y = 32.0  # Will be set from display
        
        # Trail system
        self.trail: deque = deque(maxlen=100)  # Maximum 100 trail points
        self.trail_fade_rate = 0.03
        self.trail_spacing = 2  # Add trail point every N frames
        
        # No calibration needed - use raw values like tilt game
        self.frame_count = 0
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("MotionTrailApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("MotionTrailApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("MotionTrailApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("MotionTrailApp: Failed to initialize LCD")
                return False
            
            # Initialize ball position
            self.ball_x = self.display_width // 2
            self.ball_y = self.display_height // 2
            
            # Draw initial frame
            self._draw_trail()
            
            return True
        
        except Exception as e:
            print(f"MotionTrailApp initialization error: {e}")
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
            print(f"MotionTrailApp: MPU6050 init error: {e}")
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
            print(f"MotionTrailApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_accel(self) -> tuple:
        """Read accelerometer data from MPU6050."""
        try:
            if hasattr(self.mpu6050, 'acceleration'):
                accel = self.mpu6050.acceleration
                return (accel[0], accel[1], accel[2])
            
            elif hasattr(self.mpu6050, 'get_accel_data'):
                accel = self.mpu6050.get_accel_data()
                return (accel['x'], accel['y'], accel['z'])
            
            else:
                return self._read_mpu6050_accel_basic()
        
        except Exception as e:
            print(f"MotionTrailApp: Error reading MPU6050: {e}")
            return (0.0, 0.0, 9.8)
    
    def _read_mpu6050_accel_basic(self) -> tuple:
        """Basic I2C accelerometer read."""
        try:
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x3B, 6)
            
            accel_x = (data[0] << 8 | data[1])
            if accel_x > 32767:
                accel_x -= 65536
            accel_x = accel_x / 16384.0
            
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
            print(f"MotionTrailApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 1.0)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display using display abstraction layer."""
        try:
            from PIL import Image, ImageDraw
            
            self.display = DisplayFactory.create_display(self.lcd_device)
            if not self.display:
                print("MotionTrailApp: Failed to create display adapter")
                return False
            
            self.display_width, self.display_height = self.display.get_size()
            
            # Initialize ball position and center
            self.center_x = self.display_width // 2
            self.center_y = self.display_height // 2
            self.ball_x = self.center_x
            self.ball_y = self.center_y
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            self.display.clear()
            return True
        
        except Exception as e:
            print(f"MotionTrailApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update motion trail."""
        if not self.running:
            return
        
        try:
            self.frame_count += 1
            
            # Read accelerometer
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            
            # Calculate tilt directly from accelerometer
            # MPU6050 returns values in "g" (gravity units)
            # When flat: X≈0, Y≈0, Z≈1g
            # When tilted: X and Y show tilt angle
            # Use smaller dead zone for better sensitivity to slight tilts
            if abs(accel_x) < 0.02:  # Very small dead zone for slight tilts
                accel_x = 0.0
            if abs(accel_y) < 0.02:
                accel_y = 0.0
            
            # Calculate velocity directly from tilt (constant speed, no accumulation)
            # Velocity is recalculated each frame from tilt, so no acceleration
            # Invert Y for natural feel (tilt forward = move down)
            velocity_x = accel_x * self.speed_factor
            velocity_y = -accel_y * self.speed_factor  # Invert for natural feel
            
            # Update ball position by moving at constant speed in tilt direction
            # This keeps moving while tilted, but speed doesn't accumulate
            self.ball_x += velocity_x
            self.ball_y += velocity_y
            
            # Wrap around edges (or clamp - you can change this)
            if self.ball_x < 0:
                self.ball_x = self.display_width
            elif self.ball_x > self.display_width:
                self.ball_x = 0
            
            if self.ball_y < 0:
                self.ball_y = self.display_height
            elif self.ball_y > self.display_height:
                self.ball_y = 0
            
            # Wrap around edges
            if self.ball_x < 0:
                self.ball_x = self.display_width
            elif self.ball_x > self.display_width:
                self.ball_x = 0
            
            if self.ball_y < 0:
                self.ball_y = self.display_height
            elif self.ball_y > self.display_height:
                self.ball_y = 0
            
            # Add trail point periodically
            if self.frame_count % self.trail_spacing == 0:
                trail_point = TrailPoint(self.ball_x, self.ball_y, 1.0)
                self.trail.append(trail_point)
            
            # Update trail points (fade)
            for point in self.trail:
                point.update(self.trail_fade_rate)
            
            # Remove fully faded points
            while self.trail and self.trail[0].brightness <= 0:
                self.trail.popleft()
            
            # Draw trail
            self._draw_trail()
        
        except Exception as e:
            print(f"MotionTrailApp update error: {e}")
    
    def _draw_trail(self) -> None:
        """Draw motion trail with ball."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Draw trail (connect points with lines)
            if len(self.trail) > 1:
                prev_point = None
                for point in self.trail:
                    if point.brightness > 0:
                        # Draw point based on brightness
                        # For monochrome display, we can use dithering or size
                        size = max(1, int(point.brightness * 2))
                        
                        if prev_point is not None:
                            # Draw line connecting to previous point
                            # Line brightness based on average brightness
                            avg_brightness = (point.brightness + prev_point.brightness) / 2
                            if avg_brightness > 0.3:  # Only draw if bright enough
                                self.draw.line(
                                    (
                                        int(prev_point.x), int(prev_point.y),
                                        int(point.x), int(point.y)
                                    ),
                                    fill=1,
                                    width=1
                                )
                        
                        # Draw point
                        if size > 1:
                            self.draw.ellipse(
                                (
                                    int(point.x) - size, int(point.y) - size,
                                    int(point.x) + size, int(point.y) + size
                                ),
                                outline=1,
                                width=1
                            )
                        else:
                            self.draw.point((int(point.x), int(point.y)), fill=1)
                        
                        prev_point = point
            
            # Draw current ball position (brightest)
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
            self.display.show_image(self.image)
        
        except Exception as e:
            print(f"MotionTrailApp draw error: {e}")
    
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
            print(f"MotionTrailApp cleanup error: {e}")

