"""Orientation Cube app - MPU6050 + LCD display.

Shows device orientation as a 2D-projected 3D cube.
Perfect for desk demos - rotate device slightly to see cube rotate.
"""

import math
from typing import Optional, List, Tuple
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo
from ..display.display_factory import DisplayFactory
from ..display.display_interface import DisplayInterface


class OrientationCubeApp(BaseApp):
    """Orientation Cube - shows device orientation as 3D cube projection."""
    
    def __init__(self):
        super().__init__()
        self.update_interval = 50  # 20 Hz for smooth updates
        self.mpu6050_device: Optional[DeviceInfo] = None
        self.lcd_device: Optional[DeviceInfo] = None
        self.mpu6050 = None
        self.display: Optional[DisplayInterface] = None
        
        # Display dimensions (will be set from display)
        self.display_width = 128
        self.display_height = 64
        self.center_x = 64
        self.center_y = 32
        
        # Cube size
        self.cube_size = 20
        
        # Orientation angles (in radians)
        self.roll = 0.0   # Rotation around X axis
        self.pitch = 0.0  # Rotation around Y axis
        self.yaw = 0.0    # Rotation around Z axis
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("OrientationCubeApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("OrientationCubeApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("OrientationCubeApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("OrientationCubeApp: Failed to initialize LCD")
                return False
            
            # Draw initial cube
            self._draw_cube()
            
            return True
        
        except Exception as e:
            print(f"OrientationCubeApp initialization error: {e}")
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
            print(f"OrientationCubeApp: MPU6050 init error: {e}")
            return False
    
    def _init_mpu6050_basic(self) -> bool:
        """Basic MPU6050 initialization via direct I2C."""
        try:
            import smbus2
            import time
            self.mpu6050_bus = smbus2.SMBus(self.mpu6050_device.bus)
            self.mpu6050_addr = self.mpu6050_device.address
            
            # Wake up MPU6050 (set PWR_MGMT_1 register to 0)
            self.mpu6050_bus.write_byte_data(self.mpu6050_addr, 0x6B, 0)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"OrientationCubeApp: Basic MPU6050 init error: {e}")
            return False
    
    def _read_mpu6050_accel(self) -> tuple:
        """Read accelerometer data from MPU6050.
        
        Returns:
            (x, y, z) accelerometer values in g
        """
        try:
            if hasattr(self.mpu6050, 'acceleration'):
                # adafruit library
                accel = self.mpu6050.acceleration
                # Convert m/s^2 to g (1g = 9.8 m/s^2)
                return (accel[0] / 9.8, accel[1] / 9.8, accel[2] / 9.8)
            
            elif hasattr(self.mpu6050, 'get_accel_data'):
                # mpu6050-raspberrypi library
                accel = self.mpu6050.get_accel_data()
                return (accel['x'], accel['y'], accel['z'])
            
            else:
                # Basic I2C read
                return self._read_mpu6050_accel_basic()
        
        except Exception as e:
            print(f"OrientationCubeApp: Error reading MPU6050: {e}")
            return (0.0, 0.0, 1.0)  # Default: gravity down
    
    def _read_mpu6050_accel_basic(self) -> tuple:
        """Basic I2C accelerometer read."""
        try:
            # MPU6050 accelerometer registers start at 0x3B
            data = self.mpu6050_bus.read_i2c_block_data(self.mpu6050_addr, 0x3B, 6)
            
            # Convert to signed integers (16-bit, two's complement)
            accel_x = (data[0] << 8 | data[1])
            if accel_x > 32767:
                accel_x -= 65536
            accel_x = accel_x / 16384.0  # Convert to g (FS_SEL=0, ±2g range)
            
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
            print(f"OrientationCubeApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 1.0)  # Return 1g down when flat
    
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
            print(f"OrientationCubeApp: Error reading gyro: {e}")
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
            print(f"OrientationCubeApp: Basic gyro read error: {e}")
            return (0.0, 0.0, 0.0)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display using display abstraction layer."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create display using factory
            self.display = DisplayFactory.create_display(self.lcd_device)
            if not self.display:
                print("OrientationCubeApp: Failed to create display adapter")
                return False
            
            # Get display dimensions
            self.display_width, self.display_height = self.display.get_size()
            self.center_x = self.display_width // 2
            self.center_y = self.display_height // 2
            
            # Adjust cube size based on display
            self.cube_size = min(self.display_width, self.display_height) // 4
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            # Try to load font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
            except:
                self.font = ImageFont.load_default()
            
            # Clear display
            self.display.clear()
            
            return True
        
        except Exception as e:
            print(f"OrientationCubeApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update(self) -> None:
        """Update orientation cube display."""
        if not self.running:
            return
        
        try:
            # Read accelerometer and gyroscope
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            gyro_x, gyro_y, gyro_z = self._read_mpu6050_gyro()
            
            # Calculate orientation from accelerometer (when stationary)
            # Roll: rotation around X axis (tilt left/right)
            self.roll = math.atan2(accel_y, accel_z)
            
            # Pitch: rotation around Y axis (tilt forward/back)
            self.pitch = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2))
            
            # Yaw: rotation around Z axis (compass direction)
            # Can't get yaw from accelerometer alone, use gyro integration or keep at 0
            # For simplicity, we'll keep yaw at 0 or use a simple integration
            
            # Draw cube
            self._draw_cube()
        
        except Exception as e:
            print(f"OrientationCubeApp update error: {e}")
    
    def _rotate_point(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Rotate a 3D point by roll, pitch, yaw.
        
        Args:
            x, y, z: 3D coordinates
            
        Returns:
            Rotated (x, y, z) coordinates
        """
        # Apply rotations in order: roll (X), pitch (Y), yaw (Z)
        
        # Roll rotation (around X axis)
        cos_r = math.cos(self.roll)
        sin_r = math.sin(self.roll)
        y_roll = y * cos_r - z * sin_r
        z_roll = y * sin_r + z * cos_r
        
        # Pitch rotation (around Y axis)
        cos_p = math.cos(self.pitch)
        sin_p = math.sin(self.pitch)
        x_pitch = x * cos_p + z_roll * sin_p
        z_pitch = -x * sin_p + z_roll * cos_p
        
        # Yaw rotation (around Z axis) - simplified, keep at 0 for now
        return (x_pitch, y_roll, z_pitch)
    
    def _project_3d_to_2d(self, x: float, y: float, z: float) -> Tuple[int, int]:
        """Project 3D point to 2D screen coordinates.
        
        Args:
            x, y, z: 3D coordinates
            
        Returns:
            (screen_x, screen_y) pixel coordinates
        """
        # Simple orthographic projection (ignore Z for depth)
        # Add slight perspective by using Z for scaling
        scale = 1.0 + z * 0.1  # Slight depth effect
        
        screen_x = int(self.center_x + x * scale)
        screen_y = int(self.center_y + y * scale)
        
        return (screen_x, screen_y)
    
    def _draw_cube(self):
        """Draw 3D cube wireframe."""
        try:
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Define cube vertices (centered at origin)
            s = self.cube_size / 2
            vertices_3d = [
                (-s, -s, -s),  # 0: back-bottom-left
                ( s, -s, -s),  # 1: back-bottom-right
                ( s,  s, -s),  # 2: back-top-right
                (-s,  s, -s),  # 3: back-top-left
                (-s, -s,  s),  # 4: front-bottom-left
                ( s, -s,  s),  # 5: front-bottom-right
                ( s,  s,  s),  # 6: front-top-right
                (-s,  s,  s),  # 7: front-top-left
            ]
            
            # Rotate and project vertices
            vertices_2d = []
            for v in vertices_3d:
                rotated = self._rotate_point(v[0], v[1], v[2])
                projected = self._project_3d_to_2d(rotated[0], rotated[1], rotated[2])
                vertices_2d.append(projected)
            
            # Define cube edges (12 edges of a cube)
            edges = [
                # Back face
                (0, 1), (1, 2), (2, 3), (3, 0),
                # Front face
                (4, 5), (5, 6), (6, 7), (7, 4),
                # Connecting edges
                (0, 4), (1, 5), (2, 6), (3, 7),
            ]
            
            # Draw edges
            for edge in edges:
                v1 = vertices_2d[edge[0]]
                v2 = vertices_2d[edge[1]]
                self.draw.line((v1[0], v1[1], v2[0], v2[1]), fill=1, width=1)
            
            # Draw angle information
            roll_deg = math.degrees(self.roll)
            pitch_deg = math.degrees(self.pitch)
            
            text_y = 2
            self.draw.text((2, text_y), f"Roll:{roll_deg:+.0f}", font=self.font, fill=1)
            text_y += 10
            self.draw.text((2, text_y), f"Pitch:{pitch_deg:+.0f}", font=self.font, fill=1)
            
            # Update display
            self.display.show_image(self.image)
        
        except Exception as e:
            print(f"OrientationCubeApp draw error: {e}")
    
    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            # Clear display using abstraction layer
            if self.display:
                self.display.clear()
                self.display.cleanup()
                self.display = None
            
            # Close I2C bus if using basic access
            if hasattr(self, 'mpu6050_bus'):
                try:
                    self.mpu6050_bus.close()
                except:
                    pass
        
        except Exception as e:
            print(f"OrientationCubeApp cleanup error: {e}")


