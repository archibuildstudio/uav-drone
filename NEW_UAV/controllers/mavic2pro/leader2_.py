from controller import Robot, Camera, GPS, Motor
import numpy as np

# Initialize the UAV
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Get devices
camera = robot.getDevice("camera")  # Make sure this matches your UAV's camera name
camera.enable(timestep)
gps = robot.getDevice("gps")
gps.enable(timestep)
imu = robot.getDevice("inertial unit")
imu.enable(timestep)

# Motors (assuming 4 rotors like a quadcopter)
motors = [
    robot.getDevice("front left propeller"),
    robot.getDevice("front right propeller"),
    robot.getDevice("rear left propeller"),
    robot.getDevice("rear right propeller")
]
for motor in motors:
    motor.setPosition(float('inf'))
    motor.setVelocity(0)

# PID control for smooth tracking
Kp = 0.1  # Proportional gain
Ki = 0.01  # Integral gain
Kd = 0.05  # Derivative gain
prev_error = 0
integral = 0

def pid_control(error):
    global prev_error, integral
    integral += error
    derivative = error - prev_error
    prev_error = error
    return Kp * error + Ki * integral + Kd * derivative

def detect_target(image):
    # Simple example: Track a red object (adjust based on your target)
    red_threshold = [200, 50, 50]
    width = camera.getWidth()
    height = camera.getHeight()
    
    # Find the center of the red object
    x_sum = 0
    y_sum = 0
    count = 0
    
    for x in range(width):
        for y in range(height):
            r, g, b = image[y][x]
            if r > red_threshold[0] and g < red_threshold[1] and b < red_threshold[2]:
                x_sum += x
                y_sum += y
                count += 1
    
    if count > 0:
        target_x = x_sum / count
        target_y = y_sum / count
        return (target_x, target_y)
    else:
        return None

# Main loop
while robot.step(timestep) != -1:
    # Get camera image
    image = camera.getImageArray()
    
    # Detect target
    target_pos = detect_target(image)
    
    if target_pos:
        target_x, target_y = target_pos
        image_center_x = camera.getWidth() / 2
        error_x = target_x - image_center_x
        
        # PID control to adjust UAV movement
        control_signal = pid_control(error_x)
        
        # Adjust motors (simplified example)
        motors[0].setVelocity(1.0 - control_signal)  # Left motor
        motors[1].setVelocity(1.0 + control_signal)  # Right motor
        motors[2].setVelocity(1.0 - control_signal)  # Left motor
        motors[3].setVelocity(1.0 + control_signal)  # Right motor
    else:
        # If no target, hover in place
        for motor in motors:
            motor.setVelocity(1.0)  # Hover speed