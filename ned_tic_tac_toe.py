from pyniryo import NiryoRobot, PoseObject, PinState
from pyniryo.vision import uncompress_image, extract_img_workspace
import cv2
import numpy as np
import random

robot = NiryoRobot('10.10.10.10')

robot.calibrate_auto()

# move_home() Function: moves Ned to it's home position
def move_home():
    home_pose = [0.14, -0.0, 0.203, 0.0, 0.759, -0.001] 
    robot.move(PoseObject(*home_pose)) # Move to home pose

# pick_piece(spot) Function: picks up a blue piece and places it at the spot provided at the parameter
def pick_piece(spot):
    blue_pickup_pose = [0.171, 0.116, 0.056, 0.933, 1.504, 1.517] # Blue coin's on Ned's left
    # 2D Matrix rows starts from row closest to Ned, columns starts from Ned's right
    drop_pose_0x0 = [0.203, -0.054, 0.08, -1.034, 1.492, -0.476] # Row 0, Column 0
    drop_pose_0x1 = [0.206, -0.008, 0.08, -0.649, 1.501, -0.017] # Row 0, Column 1
    drop_pose_0x2 = [0.207, 0.034, 0.081, 0.422, 1.466, 0.799] # Row 0, Column 2
    drop_pose_1x0 = [0.249, -0.056, 0.08, -0.703, 1.354, -0.225] # Row 1, Column 0
    drop_pose_1x1 = [0.248, -0.009, 0.08, -0.471, 1.364, 0.026] # Row 1, Column 1
    drop_pose_1x2 = [0.249, 0.035, 0.08, -0.169, 1.349, 0.278] # Row 1, Column 2
    drop_pose_2x0 = [0.29, -0.053, 0.077, -0.642, 1.031, -0.202] # Row 2, Column 0
    drop_pose_2x1 = [0.291, -0.008, 0.076, -0.592, 1.026, -0.088] # Row 2, Column 1
    drop_pose_2x2 = [0.288, 0.036, 0.078, -0.468, 1.058, 0.014] # Row 2, Column 2
    spot_pose = [] # Pose of chosen spot

    approach_height = 0.04

    blue_approach = blue_pickup_pose.copy() # Copy of blue_pickup_pose
    blue_approach[2] = blue_pickup_pose[2] + approach_height # Add approach_height to z of blue_approach
    robot.move(PoseObject(*blue_approach)) # Moves Ned to blue_approach
    robot.move(PoseObject(*blue_pickup_pose)) # Moves Ned to blue_pickup_pose
    robot.grasp_with_tool() # Pick up disc
    robot.move(PoseObject(*blue_approach)) # Moves Ned to blue_approach

    if spot == '0 0': # If spot is 0 0
        spot_pose = drop_pose_0x0 # Assign spot as drop_pose_1x1
    elif spot == '0 1': # If spot is 0 1
        spot_pose = drop_pose_0x1 # Assign spot as  drop_pose_0x1
    elif spot == '0 2': # If spot is 0 2
        spot_pose = drop_pose_0x2 # Assign spot as  drop_pose_0x2
    elif spot == '1 0': # If spot is 1 0
        spot_pose = drop_pose_1x0 # Assign spot as drop_pose_1x0
    elif spot == '1 1':  # If spot is 1 1
        spot_pose = drop_pose_1x1 # Assign spot as drop_pose_1x1
    elif spot == '1 2': # If spot is 1 2
        spot_pose = drop_pose_1x2 # Assign spot as drop_pose_1x2
    elif spot == '2 0': # If spot is 2 0
        spot_pose = drop_pose_2x0 # Assign spot as drop_pose_2x0
    elif spot == '2 1': # If spot is 2 1
        spot_pose = drop_pose_2x1 # Assign spot as drop_pose_2x1
    elif spot == '2 2': # If spot is 2 2
        spot_pose = drop_pose_2x2 # Assign spot as drop_pose_2x2
    else:
        print("Invalid spot.") # Error message

    spot_approach = spot_pose.copy() # Copy of spot_pose
    spot_approach[2] = spot_approach[2] + approach_height # Add approach_height to z of spot_approach
    robot.move(PoseObject(*spot_approach)) # Move to spot_approach
    robot.move(PoseObject(*spot_pose)) # Move to spot_pose
    robot.release_with_tool() # Release disc
    robot.move(PoseObject(*spot_approach)) # Move to spot_approach
    
    move_home() # Move to home

# take_image() Function: moves Ned to observation_pose, waits for 'Finished' button to be pressed, takes an image of the board, crops the board into sections, creates blue and red masks for each section, and creates a 2D list of board, by appending x and o's to list if blue or red is found in each section
def take_image():
    observation_pose = [0.152, 0.011, 0.224, 1.421, 1.507, 1.41] # Observation pose
    # Insert code to move to the observation pose
    robot.move(PoseObject(*observation_pose)) 

    while True: 
        # Example: read digital input from GPIO_1
        button = robot.digital_read('DI2')
        # print("Button Press:", button==PinState.HIGH)
        if button == PinState.HIGH:
            break

    # Getting image
    img_compressed = robot.get_img_compressed() # Compress image
    # Uncompressing image
    img = uncompress_image(img_compressed) # Uncompress image

    # Saving
    cv2.imwrite("output_image1.png", img)

    im_work = extract_img_workspace(img, workspace_ratio=1.0) 

    s = 10 # Border width
    l = 60 # Length/width of section

    board_sections = [] # List of board sections

    # Nested for loop 
    for i in range(3):# Outer loop 
        for j in range(3): # Inner loop 
            y_1 = (s + (i * l)) # Starting height
            y_2 = (s + ((i + 1) * l)) # Ending height
            x_1 = (s + (j * l)) # Starting width
            x_2 = (s + ((j + 1) * l)) # Ending width
            sec_img = im_work[y_1:y_2 , x_1:x_2] # Crop section of board
            board_sections.append(sec_img) # Append section to board_sections

    board_list = [] # List of board's places
    for i, section in enumerate(board_sections): # Loop through board_sections
        image = cv2.resize(section, (300, 300)) # Resize image of section
        total_pixels = image.shape[0] * image.shape[1] # Calculate image's total pixels

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Convert image to HSV

        blue_lower = np.array([100, 100, 100]) # Blue's HSV lower range
        blue_upper = np.array([130, 255, 255]) # Blue's HSV upper range

        blue_mask = cv2.inRange(hsv_image, blue_lower, blue_upper) # Creates of mask of hsv_image, turning the blue pixels within the range of blue_lower and blue_upper, white 
        blue_pixels = cv2.countNonZero(blue_mask) # Counts the number or non-zero pixels in blue_mask
        percent_blue = (blue_pixels/total_pixels) * 100 # Calculates percentage of blue pixels in blue_mask

        # Lower Red Range
        lower_red1 = np.array([0, 100, 100]) # Red's HSV 1st lower range
        upper_red1 = np.array([10, 255, 255]) # Red's HSV 1st upper range

        # Upper Red Range
        lower_red2 = np.array([160, 100, 100]) # Red's HSV 2nd upper range
        upper_red2 = np.array([179, 255, 255]) # Red's HSV 2nd lower range

        red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1) # Creates of mask of hsv_image, turning the red pixels within the range of  red_lower1 and red_upper1, white 
        red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2) # Creates of mask of hsv_image, turning the red pixels within the range of  red_lower2 and red_upper2, white
        red_mask = cv2.bitwise_or(red_mask1, red_mask2) # Combines red_mask1 and red_mask2
        red_pixels = cv2.countNonZero(red_mask) # Counts the number or non-zero pixels in blue_mask
        percent_red = (red_pixels/total_pixels) * 100 # Calculates percentage of red pixels in red_mask

        if percent_blue > 20: # If percent_blue is greater than 20%
            board_list.append('o') # Add 'o' to board_list
        elif percent_red > 20: # If percent_red is greater than 20%
            board_list.append('x') # Add 'x' to board_list
        else: # If percent_blue and percent_red are less than 20%
            board_list.append('-') # Add 'x' to board_list

    board_array = np.array(board_list) # Convert board_list to an array
    board_array = board_array[::-1] # Reverse board_array
    board_2d_array = np.reshape(board_array, (3, 3)) # Reshapes board_array into 2D array of three arrays, each with 3 elements
    board_2d_list = list(board_2d_array) # Convert board_2d_array back to list
    return board_2d_list # Return 2D list of board

# print_board(board) Function: takes in 2D list of board and prints out layout of board with indicies on edges
def print_board(board):
    print("Current Board: ")
    print('   0 1 2') # Output board indicies
    for i, row in enumerate(board): # Loop through each array in 2D array, enumerating each row
        print(f'{i}  {row[0]} {row[1]} {row[2]}') # Print all elements within array

# ned_play(board) Function: takes in 2D list of board and randomly selects a spot for Ned to take, if spot is taken, a new position is chosen until an emtpy spot is found
def ned_play(board):
    rand_row = random.randint(0, 2) # Assigns random column coordinate from 1-2
    rand_column = random.randint(0, 2) # Assigns random row coordinate from 1-2

    while board[rand_row][rand_column]  == 'x' or board[rand_row][rand_column]  == 'o': # While accessed element is not 'x' or 'o' (a coordinate already played)
        rand_row = random.randint(0, 2) # Reassigns random column
        rand_column = random.randint(0, 2) # Reassigns random row

    return f"{rand_row} {rand_column}" # Return string of rand_row and rand_column separated by a space

# play() Function: has Ned chose a spot and place a disc at that spot
def play(board): 
    print("Ned's turn.")
    spot = ned_play(board) # Runs ned_play function and assigns returned string as spot 
    pick_piece(spot) # Runs pick_piece() function on spot 

    spot_list = spot.split() # Splits spot string by default spaces
    row = int(spot_list[0]) # Assigns 1st list element typecasted as an integer as row
    column = int(spot_list[1]) # Assigns 2nd list element typecasted as an integer as row
    board[row][column] = 'o' # Assigns board element at row and column as 'o'

    print(f"Ned placed an 'o' {spot}") # Outputs spot
    return board

# check_win(board) Function: checks 2D list of board for a win/loss or filled board
def check_win(board):
    # Ned's reaction poses
    win_pose_1 = [0.151, 0.0, 0.265, -0.333, 0.9, 0.008]
    win_pose_2 = [0.161, -0.0, 0.302, -0.347, 0.001, -0.003]
    loss_pose_1 = [0.094, -0.106, 0.225, -0.697, 0.654, -0.828]
    loss_pose_2 = [0.108, 0.089, 0.221, -0.775, 0.671, 0.699]
    draw_pose_1 = [0.136, -0.02, 0.223, -0.439, 0.629, -0.074]
    draw_pose_2 = [0.135, -0.01, 0.219, -0.821, 0.659, -0.128]

    winner = ''
    # If element at the first position in each row/column is not a dash (an empty spot in the game)
    if board[0][0] != '-' and board[0][0] == board[0][1] and board[0][1] == board[0][2]: # If all elements in row 1 are equal
        winner = board[0][0] # Return element
    elif board[1][0] != '-' and board[1][0] == board[1][1] and board[1][1] == board[1][2]: # If all all elements in row 2 are equal
        winner = board[1][0]
    elif board[2][0] != '-' and board[2][0] == board[2][1] and board[2][1] == board[2][2]: # If all all elements in row 3 are equal
        winner = board[2][0]
    elif board[0][0] != '-' and board[0][0] == board[1][0] and board[1][0] == board[2][0]: # If all elements in column 1 are equal
        winner =  board[0][0]
    elif board[0][1] != '-' and board[0][1] == board[1][1] and board[1][1] == board[2][1]: # If all elements in column 2 are equal
        winner = board[0][1]
    elif board[0][2] != '-' and board[0][2] == board[1][2] and board[1][2] == board[2][2]: # If all elements in column 3 are equal
        winner = board[0][2]
    elif board[0][0] != '-' and board[0][0] == board[1][1] and board[1][1] == board[2][2]: # If all elements in diagonal starting from left
        winner = board[0][0]
    elif board[2][0] != '-' and board[2][0] == board[1][1] and board[1][1] == board[0][2]: # If all elements in diagonal starting from right
        winner = board[2][0]
    else: # If none of the rows/columns all have the same elements
        winner = '' # Return an empty string

    if winner == 'o': # If winner is 'o'
        print("Ned won! You lost.")
        robot.move(PoseObject(*win_pose_1)) # Move Ned to win_pose_1
        robot.move(PoseObject(*win_pose_1))
        robot.move(PoseObject(*win_pose_2)) # Move Ned to win_pose_2
        robot.move(PoseObject(*win_pose_2))
        robot.move(PoseObject(*win_pose_1))
        robot.move(PoseObject(*win_pose_1))
        return 1 # Return 1 (true)
    elif winner == 'x': # If winner is 'x'
        print("You won! Ned lost.") 
        robot.move(PoseObject(*loss_pose_1)) # Move Ned to loss_pose_1
        robot.move(PoseObject(*loss_pose_2)) # Move Ned to loss_pose_2
        robot.move(PoseObject(*loss_pose_1))
        return 1  
    else:
        for i in range(0, 3):
            for j in range(0, 3): 
                if board[i][j] == 'x' or board[i][j] == 'o': # If accessed element on board is either 'x' or 'o' (a taken coordinate)
                    continue # Continue onto next loop
                elif board[i][j] == '-': # If accessed element on board is '-' (empty)
                    return 0 # Return 0 (false)
        print("Draw!")
        robot.move(PoseObject(*draw_pose_1)) # Move Ned to draw_pose_1
        robot.move(PoseObject(*draw_pose_2)) # Move Ned to draw_pose_2
        robot.move(PoseObject(*draw_pose_1)) 
        return 1

def main():
    print("Let's play tic tac toe with Ned!")
    move_home() # Move Ned home
    winner = 0 # Assign winner as 0
    board = [['-', '-', '-'],['-', '-', '-'],['-', '-', '-']]
    print_board(board) # Call print_board function on board
    while winner == 0 : # While winner is 0
        board = play(board) # Call play function on board and assign returned 2D list as board
        print_board(board) # Call print_board function on board
        winner = check_win(board) # Call check_win function on board and assign returned 2D list as winner
        if winner == 1: # If there is a winner or the board is filled 
            break # Break out of loop
        print("Your turn! Press the 'Finished' button once you've placed a red disc on a spot.")
        board = take_image() # Run take_image Function and assign returned 2D list as board
        print_board(board) # Call print_board function on board
        winner = check_win(board)
        if winner == 1: # If there is a winner or the board is filled 
            break # Break out of loop
    move_home() # Move Ned home

# Testing move_home()
# move_home()
# Works

# # Testing pick_piece()
# pick_piece('0 0')
# pick_piece('0 1')
# pick_piece('0 2')
# pick_piece('1 0')
# pick_piece('1 1')
# pick_piece('1 2')
# pick_piece('2 0')
# pick_piece('2 1')
# pick_piece('2 2')
# Works

# # Testing print_board()
# board = [['-', 'x', 'o'],['-', 'x', 'o'],['-', 'x', 'o']]
# print_board(board)
# Works

# # Testing take_image()
# board = take_image()
# print_board(board)
# Works 

# # Testing ned_play()
# board = [['-', 'x', 'o'],['-', 'x', 'o'],['-', 'x', 'o']]
# print(ned_play(board))
# Works

# # Testing play()
# play()
# Works

# # Testing check_win()
# board = [['-', 'o', 'o'],['-', '-', 'o'],['x', 'x', 'x']]
# print(check_win(board))
# board = [['-', 'o', 'x'],['-', 'o', 'o'],['-', 'x', 'x']]
# print(check_win(board))
# board = [['x', 'o', 'x'],['x', 'o', 'o'],['o', 'x', 'x']]
# print(check_win(board))
# board = [['x', 'o', 'o'],['x', 'o', 'o'],['o', 'x', 'o']]
# print(check_win(board)) 

main()
