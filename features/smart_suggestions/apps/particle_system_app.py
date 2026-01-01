"""Particle System app - MPU6050 + LCD display.

Creates particles that respond to tilt/acceleration with visual trails.
Perfect for desk demos - slight tilts create flowing particle patterns.
"""

import math
import random
from typing import Optional, List, Tuple
from ..app_framework import BaseApp
from ..device_detector import DeviceInfo
from ..display.display_factory import DisplayFactory
from ..display.display_interface import DisplayInterface


class Particle:
    """A single particle in the system."""
    
    def __init__(self, x: float, y: float, display_width: int, display_height: int):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.life = 1.0  # Life remaining (1.0 = full, 0.0 = dead)
        self.decay = 0.02  # Life decay per frame
        self.display_width = display_width
        self.display_height = display_height
    
    def update(self, accel_x: float, accel_y: float, gravity: float = 0.3):
        """Update particle position based on acceleration."""
        # Apply acceleration to velocity
        self.vx += accel_x * 0.5
        self.vy += accel_y * 0.5
        
        # Apply gravity (downward)
        self.vy += gravity
        
        # Apply damping
        self.vx *= 0.95
        self.vy *= 0.95
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Wrap around edges
        if self.x < 0:
            self.x = self.display_width
        elif self.x > self.display_width:
            self.x = 0
        
        if self.y < 0:
            self.y = self.display_height
        elif self.y > self.display_height:
            self.y = 0
        
        # Decay life
        self.life -= self.decay
        if self.life <= 0:
            self.life = 0
    
    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.life > 0


class ParticleSystemApp(BaseApp):
    """Particle System - particles that respond to tilt/acceleration."""
    
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
        
        # Particle system
        self.particles: List[Particle] = []
        self.max_particles = 30
        self.spawn_rate = 0.5  # Probability of spawning new particle per frame
        
        # Calibration
        self.accel_offset_x = 0.0
        self.accel_offset_y = 0.0
        self.calibration_frames = 30
        self.calibration_count = 0
    
    def _initialize(self) -> bool:
        """Initialize MPU6050 and LCD."""
        try:
            # Find devices
            self.mpu6050_device = self.find_device("IMU")
            self.lcd_device = self.find_device("DISPLAY")
            
            if not self.mpu6050_device:
                print("ParticleSystemApp: MPU6050 not found")
                return False
            
            if not self.lcd_device:
                print("ParticleSystemApp: LCD display not found")
                return False
            
            # Initialize MPU6050
            if not self._init_mpu6050():
                print("ParticleSystemApp: Failed to initialize MPU6050")
                return False
            
            # Initialize LCD
            if not self._init_lcd():
                print("ParticleSystemApp: Failed to initialize LCD")
                return False
            
            # Initialize particles
            self._init_particles()
            
            # Draw initial frame
            self._draw_particles()
            
            return True
        
        except Exception as e:
            print(f"ParticleSystemApp initialization error: {e}")
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
            print(f"ParticleSystemApp: MPU6050 init error: {e}")
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
            print(f"ParticleSystemApp: Basic MPU6050 init error: {e}")
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
            print(f"ParticleSystemApp: Error reading MPU6050: {e}")
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
            print(f"ParticleSystemApp: Basic MPU6050 read error: {e}")
            return (0.0, 0.0, 1.0)
    
    def _init_lcd(self) -> bool:
        """Initialize LCD display using display abstraction layer."""
        try:
            from PIL import Image, ImageDraw
            
            self.display = DisplayFactory.create_display(self.lcd_device)
            if not self.display:
                print("ParticleSystemApp: Failed to create display adapter")
                return False
            
            self.display_width, self.display_height = self.display.get_size()
            
            # Create image and draw context
            self.image = Image.new('1', (self.display_width, self.display_height))
            self.draw = ImageDraw.Draw(self.image)
            
            self.display.clear()
            return True
        
        except Exception as e:
            print(f"ParticleSystemApp: LCD init error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_particles(self):
        """Initialize particle system."""
        self.particles = []
        # Start with a few particles
        for _ in range(5):
            x = random.uniform(0, self.display_width)
            y = random.uniform(0, self.display_height)
            particle = Particle(x, y, self.display_width, self.display_height)
            self.particles.append(particle)
    
    def update(self) -> None:
        """Update particle system."""
        if not self.running:
            return
        
        try:
            # Read accelerometer
            accel_x, accel_y, accel_z = self._read_mpu6050_accel()
            
            # Calibrate on first few frames
            if self.calibration_count < self.calibration_frames:
                self.accel_offset_x += accel_x
                self.accel_offset_y += accel_y
                self.calibration_count += 1
                
                if self.calibration_count == self.calibration_frames:
                    self.accel_offset_x /= self.calibration_frames
                    self.accel_offset_y /= self.calibration_frames
                    print(f"ParticleSystemApp: Calibrated offsets: ({self.accel_offset_x:.3f}, {self.accel_offset_y:.3f})")
            
            # Calculate relative acceleration (remove static offset)
            rel_accel_x = accel_x - self.accel_offset_x
            rel_accel_y = accel_y - self.accel_offset_y
            
            # Scale acceleration for particle movement
            accel_scale = 0.3
            particle_accel_x = rel_accel_x * accel_scale
            particle_accel_y = rel_accel_y * accel_scale
            
            # Update existing particles
            for particle in self.particles[:]:
                particle.update(particle_accel_x, particle_accel_y)
                if not particle.is_alive():
                    self.particles.remove(particle)
            
            # Spawn new particles
            if len(self.particles) < self.max_particles:
                if random.random() < self.spawn_rate:
                    x = random.uniform(0, self.display_width)
                    y = random.uniform(0, self.display_height)
                    particle = Particle(x, y, self.display_width, self.display_height)
                    self.particles.append(particle)
            
            # Draw particles
            self._draw_particles()
        
        except Exception as e:
            print(f"ParticleSystemApp update error: {e}")
    
    def _draw_particles(self) -> None:
        """Draw particles with trails."""
        try:
            from PIL import Image, ImageDraw
            
            # Clear image
            self.draw.rectangle(
                (0, 0, self.display_width, self.display_height),
                fill=0
            )
            
            # Draw particles with size based on life
            for particle in self.particles:
                if particle.is_alive():
                    # Size based on life (larger when more alive)
                    size = max(1, int(particle.life * 3))
                    
                    # Draw particle as circle
                    x = int(particle.x)
                    y = int(particle.y)
                    
                    # Draw main particle
                    if size > 1:
                        self.draw.ellipse(
                            (x - size, y - size, x + size, y + size),
                            fill=1
                        )
                    else:
                        self.draw.point((x, y), fill=1)
                    
                    # Draw trail (smaller, dimmer)
                    if particle.life < 0.7:
                        trail_size = max(1, int(particle.life * 2))
                        self.draw.ellipse(
                            (x - trail_size, y - trail_size, x + trail_size, y + trail_size),
                            outline=1
                        )
            
            # Update display
            self.display.show_image(self.image)
        
        except Exception as e:
            print(f"ParticleSystemApp draw error: {e}")
    
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
            print(f"ParticleSystemApp cleanup error: {e}")


