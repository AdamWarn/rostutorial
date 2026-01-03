# RobotStatus.msg - Overall robot state

# Battery information
float32 battery_voltage
float32 battery_percentage

# Cleaning state
bool is_cleaning
float32 coverage_percentage

# Position (odometry)
float32 x
float32 y
float32 yaw

# Status
string mode  # "idle", "cleaning", "charging", "error"
string error_message
