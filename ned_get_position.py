from pyniryo import NiryoRobot

robot = NiryoRobot('10.10.10.10')

robot.calibrate_auto()

# Your code here
joint_read = robot.get_joints()
# Convert to list
joint_read_list = list(joint_read)
rounded_joint_list = [] # Create empty list
# Round all values to 3 decimal places
for element in joint_read_list: # Loop through all elements in joint_read_list
    rounded_joint_list.append(round(element, 3)) # Round element to 3 decimal places, append to rounded_joint_list
# Print out list
print(f"Joint Coordinates: {rounded_joint_list}")

pose_read = robot.get_pose()
# Convert to list
pose_read_list = list(pose_read)
rounded_pose_list = [] # Create empty list
# Round all values to 3 decimal places
for element in pose_read_list: # Loop through all elements in joint_read_list
    rounded_pose_list.append(round(element, 3)) # Round element to 3 decimal places, append to rounded_joint_list
# Print out list
print(f"Pose Coordinates: {rounded_pose_list}")
