# Chapter 20: Hardware Integration & Real Robot Deployment

**Goal**: Connect real sensors, motors, and deploy your code to a physical robot!

---

## 📖 From Simulation to Reality

**What changes**:
- Gazebo sensors → Real sensors
- Simulated motors → Real motors
- Perfect environment → Real-world noise
- Instant resets → Careful testing

**Good news**: Most of your code stays the same!

---

## 🎯 Understanding Hardware Basics

### What is a Microcontroller?

A **microcontroller** is a small computer that controls hardware.

**Examples**:
- **Arduino**: Simple, beginner-friendly
- **Raspberry Pi Pico**: More powerful
- **ESP32**: Has WiFi built-in
- **Teensy**: Very fast

**What it does**:
- Reads sensors
- Controls motors
- Sends data to main computer (like Raspberry Pi)

---

### Communication: How Computers Talk to Hardware

**Serial Communication** (most common):

```
Computer (ROS2) ←── USB Cable ──→ Arduino (Motors/Sensors)
```

**Think of it like**:
- Sending text messages back and forth
- One character at a time
- Very fast (usually 115200 "baud" = bits per second)

---

## 🤖 Common Robot Hardware

### 1. LiDAR Sensors

**Popular models**:
- **RPLiDAR A1**: Budget ($99)
- **RPLiDAR A2**: Better range ($400)
- **YDLIDAR X4**: Alternative ($120)

**Connection**:
```bash
# Most connect via USB
# Appears as /dev/ttyUSB0 or similar

# Give permission
sudo chmod 666 /dev/ttyUSB0

# Or add yourself to dialout group (permanent)
sudo usermod -a -G dialout $USER
# Then log out and back in
```

**ROS2 Driver**:
```bash
# Install RPLIDAR driver
sudo apt install ros-jazzy-rplidar-ros

# Run it
ros2 run rplidar_ros rplidar_node --ros-args -p serial_port:=/dev/ttyUSB0
```

---

### 2. Motor Controllers

**Types**:
- **L298N**: Simple, dual motor, cheap ($5)
- **Sabertooth**: Powerful, expensive ($120)
- **Pololu**: Mid-range ($30)

**Connection**:
- Arduino controls motors via pins
- Arduino talks to ROS2 computer via USB/Serial

---

### 3. Wheel Encoders

**What they do**: Count wheel rotations

**Types**:
- **Hall effect**: Magnets on wheel
- **Optical**: Light sensors reading slots

**Why needed**: Calculate odometry (robot position)

```
Encoder counts → Wheel rotation → Distance traveled → Robot position
```

---

## 💻 Arduino to ROS2 Bridge

### Understanding Serial Communication

**Arduino side** (C++):
```cpp
void setup() {
  // Start serial at 115200 baud
  Serial.begin(115200);
}

void loop() {
  // Send a message
  Serial.println("Hello from Arduino!");
  delay(1000);  // Wait 1 second
}
```

**ROS2 side** (Python):
```python
import serial

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Read message
line = ser.readline().decode('utf-8').strip()
print(f"Arduino said: {line}")
```

---

### Using micro-ROS (Advanced)

**micro-ROS** lets Arduino run ROS2 directly!

```bash
# Install micro-ROS (on main computer)
sudo apt install ros-jazzy-micro-ros-setup
```

**Arduino code** becomes ROS2 node:
```cpp
#include <micro_ros_arduino.h>
#include <std_msgs/msg/int32.h>

rcl_publisher_t publisher;
std_msgs__msg__Int32 msg;

void setup() {
  // Initialize micro-ROS
  set_microros_transports();
  
  // Create publisher
  rclc_publisher_init_default(
    &publisher,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "arduino_data");
}

void loop() {
  msg.data = analogRead(A0);  // Read sensor
  rcl_publish(&publisher, &msg, NULL);
  delay(100);
}
```

---

## 🚗 Motor Control Example

### Simple Differential Drive

**Hardware needed**:
- 2 motors with encoders
- Motor driver (L298N)
- Arduino
- Raspberry Pi (running ROS2)

---

### Arduino Code (Motor Controller)

```cpp
// Motor pins
#define LEFT_MOTOR_FWD 5
#define LEFT_MOTOR_REV 6
#define RIGHT_MOTOR_FWD 9
#define RIGHT_MOTOR_REV 10

// Encoder pins
#define LEFT_ENCODER_A 2
#define LEFT_ENCODER_B 3
#define RIGHT_ENCODER_A 18
#define RIGHT_ENCODER_B 19

// Encoder counts
volatile long left_count = 0;
volatile long right_count = 0;

void setup() {
  Serial.begin(115200);
  
  // Motor pins as output
  pinMode(LEFT_MOTOR_FWD, OUTPUT);
  pinMode(LEFT_MOTOR_REV, OUTPUT);
  pinMode(RIGHT_MOTOR_FWD, OUTPUT);
  pinMode(RIGHT_MOTOR_REV, OUTPUT);
  
  // Encoder pins as input
  pinMode(LEFT_ENCODER_A, INPUT_PULLUP);
  pinMode(LEFT_ENCODER_B, INPUT_PULLUP);
  pinMode(RIGHT_ENCODER_A, INPUT_PULLUP);
  pinMode(RIGHT_ENCODER_B, INPUT_PULLUP);
  
  // Attach interrupts (count encoder pulses)
  attachInterrupt(digitalPinToInterrupt(LEFT_ENCODER_A), 
                  leftEncoderISR, RISING);
  attachInterrupt(digitalPinToInterrupt(RIGHT_ENCODER_A), 
                  rightEncoderISR, RISING);
}

void loop() {
  // Check for commands from ROS2
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    parseCommand(cmd);
  }
  
  // Send encoder data back to ROS2
  Serial.print("E:");
  Serial.print(left_count);
  Serial.print(",");
  Serial.println(right_count);
  
  delay(50);  // 20Hz update
}

void parseCommand(String cmd) {
  // Expected format: "M:left_speed,right_speed"
  // Example: "M:100,100" = both forward at speed 100
  
  if (cmd.startsWith("M:")) {
    int comma = cmd.indexOf(',');
    int left_speed = cmd.substring(2, comma).toInt();
    int right_speed = cmd.substring(comma + 1).toInt();
    
    setMotorSpeed(left_speed, right_speed);
  }
}

void setMotorSpeed(int left, int right) {
  // Left motor
  if (left >= 0) {
    analogWrite(LEFT_MOTOR_FWD, left);
    analogWrite(LEFT_MOTOR_REV, 0);
  } else {
    analogWrite(LEFT_MOTOR_FWD, 0);
    analogWrite(LEFT_MOTOR_REV, -left);
  }
  
  // Right motor
  if (right >= 0) {
    analogWrite(RIGHT_MOTOR_FWD, right);
    analogWrite(RIGHT_MOTOR_REV, 0);
  } else {
    analogWrite(RIGHT_MOTOR_FWD, 0);
    analogWrite(RIGHT_MOTOR_REV, -right);
  }
}

// Interrupt functions (called when encoder ticks)
void leftEncoderISR() {
  left_count++;
}

void rightEncoderISR() {
  right_count++;
}
```

---

### ROS2 Node (Serial Bridge)

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import serial
import math


class ArduinoBridge(Node):
    """
    Bridge between ROS2 and Arduino.
    
    Subscribes to /cmd_vel and sends motor commands to Arduino.
    Reads encoder data from Arduino and publishes odometry.
    """
    
    def __init__(self):
        super().__init__('arduino_bridge')
        
        # Parameters
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('wheel_separation', 0.3)  # meters
        self.declare_parameter('wheel_radius', 0.05)     # meters
        self.declare_parameter('encoder_ticks_per_rev', 1000)
        
        port = self.get_parameter('serial_port').value
        baud = self.get_parameter('baud_rate').value
        
        # Open serial connection
        try:
            self.serial = serial.Serial(port, baud, timeout=1)
            self.get_logger().info(f'Connected to Arduino on {port}')
        except Exception as e:
            self.get_logger().error(f'Failed to connect: {e}')
            return
        
        # Subscribe to velocity commands
        self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Publish odometry
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        
        # Read from Arduino
        self.create_timer(0.05, self.read_serial)  # 20Hz
        
        # Odometry state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_left_count = 0
        self.last_right_count = 0
    
    def cmd_vel_callback(self, msg):
        """
        Convert Twist message to motor speeds.
        
        msg.linear.x = forward speed (m/s)
        msg.angular.z = rotation speed (rad/s)
        """
        # Get wheel speeds from twist command
        linear = msg.linear.x
        angular = msg.angular.z
        
        wheel_sep = self.get_parameter('wheel_separation').value
        
        # Differential drive kinematics
        # v_left = linear - (angular * wheel_separation / 2)
        # v_right = linear + (angular * wheel_separation / 2)
        
        v_left = linear - (angular * wheel_sep / 2.0)
        v_right = linear + (angular * wheel_sep / 2.0)
        
        # Convert m/s to motor PWM (0-255)
        # This is robot-specific, tune these values!
        max_speed = 0.5  # m/s
        left_pwm = int((v_left / max_speed) * 255)
        right_pwm = int((v_right / max_speed) * 255)
        
        # Clamp to -255 to 255
        left_pwm = max(-255, min(255, left_pwm))
        right_pwm = max(-255, min(255, right_pwm))
        
        # Send to Arduino
        cmd = f"M:{left_pwm},{right_pwm}\n"
        self.serial.write(cmd.encode())
        
        self.get_logger().debug(f'Sent: {cmd.strip()}')
    
    def read_serial(self):
        """Read encoder data from Arduino."""
        if self.serial.in_waiting > 0:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                
                # Parse encoder data: "E:1234,5678"
                if line.startswith('E:'):
                    counts = line[2:].split(',')
                    left_count = int(counts[0])
                    right_count = int(counts[1])
                    
                    # Update odometry
                    self.update_odometry(left_count, right_count)
                    
            except Exception as e:
                self.get_logger().error(f'Serial read error: {e}')
    
    def update_odometry(self, left_count, right_count):
        """Calculate robot position from encoder counts."""
        # Get parameters
        wheel_radius = self.get_parameter('wheel_radius').value
        wheel_sep = self.get_parameter('wheel_separation').value
        ticks_per_rev = self.get_parameter('encoder_ticks_per_rev').value
        
        # Calculate distance traveled by each wheel
        left_delta = left_count - self.last_left_count
        right_delta = right_count - self.last_right_count
        
        # Convert ticks to meters
        meters_per_tick = (2 * math.pi * wheel_radius) / ticks_per_rev
        left_dist = left_delta * meters_per_tick
        right_dist = right_delta * meters_per_tick
        
        # Calculate robot movement
        dist = (left_dist + right_dist) / 2.0
        dtheta = (right_dist - left_dist) / wheel_sep
        
        # Update pose
        self.x += dist * math.cos(self.theta + dtheta/2.0)
        self.y += dist * math.sin(self.theta + dtheta/2.0)
        self.theta += dtheta
        
        # Normalize theta
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        # Publish odometry
        self.publish_odometry()
        
        # Update last counts
        self.last_left_count = left_count
        self.last_right_count = right_count
    
    def publish_odometry(self):
        """Publish current odometry."""
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        # Position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        
        # Orientation (convert theta to quaternion)
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, self.theta)
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        
        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridge()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## 🔧 Calibration

### Why Calibrate?

Real hardware has errors:
- Wheels aren't perfectly round
- Motors have different strengths
- Encoders may skip counts

**Calibration** measures and corrects these.

---

### Wheel Diameter Calibration

```python
# 1. Command robot to drive forward 1 meter
# 2. Measure actual distance traveled
# 3. Calculate correction factor

commanded_distance = 1.0  # meters
actual_distance = 0.95    # measured with tape measure

correction_factor = actual_distance / commanded_distance
# = 0.95

# Apply correction
wheel_radius_corrected = wheel_radius * correction_factor
```

---

### Motor Balance Calibration

```python
# If robot drifts to one side when going "straight"
# One motor is stronger

# Test: drive straight, measure drift angle
# Adjust motor speeds:

if robot_drifts_left:
    left_motor_multiplier = 0.95  # Slow down left
    right_motor_multiplier = 1.0
```

---

## 🎯 Safety Considerations

### Emergency Stop

```python
import RPi.GPIO as GPIO

class SafetyMonitor(Node):
    def __init__(self):
        super().__init__('safety_monitor')
        
        # E-stop button on GPIO pin 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Check button every 0.1 seconds
        self.create_timer(0.1, self.check_estop)
        
        # Publisher to stop robot
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
    
    def check_estop(self):
        """Check if emergency stop is pressed."""
        if GPIO.input(17) == GPIO.LOW:  # Button pressed
            self.get_logger().error('EMERGENCY STOP!')
            
            # Stop robot
            stop_msg = Twist()  # All zeros
            self.cmd_pub.publish(stop_msg)
```

---

### Battery Monitor

```python
class BatteryMonitor(Node):
    def __init__(self):
        super().__init__('battery_monitor')
        
        # Read battery voltage from ADC
        # (Assumes voltage divider and MCP3008 ADC)
        
        self.create_timer(5.0, self.check_battery)
    
    def check_battery(self):
        """Check battery voltage."""
        voltage = self.read_battery_voltage()
        
        percentage = self.voltage_to_percentage(voltage)
        
        if percentage < 20:
            self.get_logger().error(f'Battery LOW: {percentage}%')
            # Could trigger return-to-dock here
        
        self.get_logger().info(f'Battery: {percentage}% ({voltage:.2f}V)')
    
    def read_battery_voltage(self):
        # Read from ADC (implementation depends on hardware)
        # This is a placeholder
        return 11.5  # volts
    
    def voltage_to_percentage(self, voltage):
        """Convert voltage to percentage (for 3S LiPo)."""
        # 3S LiPo: 12.6V full, 9.0V empty
        full = 12.6
        empty = 9.0
        
        percentage = ((voltage - empty) / (full - empty)) * 100
        return max(0, min(100, percentage))
```

---

## 💻 Exercises

### Exercise 20.1: Test RPLIDAR

1. Connect RPLIDAR to computer
2. Run driver: `ros2 run rplidar_ros rplidar_node`
3. Visualize in RViz
4. Compare to Gazebo simulation

### Exercise 20.2: Motor Testing

1. Connect motors to Arduino
2. Upload motor control sketch
3. Test with manual serial commands
4. Verify both forward and reverse

### Exercise 20.3: Odometry Accuracy

1. Command robot: forward 1m, rotate 90°
2. Measure actual movement
3. Calculate error
4. Tune parameters to improve

---

## 🎯 Key Takeaways

1. **Real hardware** requires drivers and calibration
2. **Serial communication** bridges Arduino to ROS2
3. **Encoders** measure wheel rotation for odometry
4. **Calibration** corrects hardware imperfections
5. **Safety** requires e-stops and monitoring
6. **micro-ROS** lets Arduino run ROS2 directly
7. **Testing** real hardware takes patience!

---

## 🚀 Next Chapter

[Chapter 21: Final Project](../chapter_21_final_project/README.md) - Integrate everything into a complete cleaning robot!

---

## 📚 Resources

- [RPLIDAR ROS](https://github.com/Slamtec/rplidar_ros)
- [micro-ROS](https://micro.ros.org/)
- [Arduino Serial](https://www.arduino.cc/reference/en/language/functions/communication/serial/)
- [Raspberry Pi GPIO](https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/)
