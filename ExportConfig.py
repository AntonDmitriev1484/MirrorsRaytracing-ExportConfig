import os
import json
import re
import sys

# PROTOCOL

# Format:  'move row col motor direction steps'
# output that line by line into a text file

# row starts from 0 -> row.size() -1
# col starts from 0 -> # mirrors per row

# motor 1 rotates up / down, motor 0 rotates left /right rotation about z
# direction 0 is -, 1 is +. so 0 is (left and down), so 1 is (right and up)
# delta position is steps / Prof. Chamberlain sent over the conversion rate.

# Update a text file: "CatotpricInput.txt"


# After I write, invoke './CatoptricController -Test'
# -Test will just be a flag that automatically goes and reads everything from my text file


# Constants

PAIR_SYS_NAME = sys.argv[1] # Command line argument specifies what config file we want to use
REGEX = "\((\d)\,(\d)\) : P=(-?\d{1,4}\.\d{1,6}) Y=(-?\d{1,4}\.\d{1,6}) R=(-?\d{1,4}\.\d{1,6})"
READ_FROM_PATH = "../"
WRITE_TO_PATH = "../"
OUTPUT_NAME = "CatoptricInput.txt"
INPUT_FILE = open(READ_FROM_PATH+PAIR_SYS_NAME+"Config.txt","r")
OUTPUT_FILE = open(WRITE_TO_PATH+OUTPUT_NAME, "w")
STEPS_TO_DEGREES_RATIO = 16.128/11.25 # 11.25 deg/ 16.128 steps ratio


def LineToCatoptricControllerCommands(line):
    match_obj = re.match(REGEX, line)

    x = int(match_obj[1])
    y = int(match_obj[2])

    pitch = float(match_obj[3])
    yaw = float(match_obj[4])

    pitch_direction = (0, 1) [pitch < 0] # scuffed ternary operator by indexing
    yaw_direction = (0, 1) [yaw < 0]

    pitch_steps = abs(pitch) * STEPS_TO_DEGREES_RATIO
    yaw_steps = abs(yaw) * STEPS_TO_DEGREES_RATIO

    # motor 1 changes pitch
    # motor 0 changes yaw

    # move row col motor direction steps
    pitch_motor_command = f'move {y} {x} 1 {pitch_direction} {pitch_steps}'
    yaw_motor_command = f'move {y} {x} 0 {yaw_direction} {yaw_steps}'

    return (pitch_motor_command, yaw_motor_command)


def LineToJSON(line):
    match_obj = re.match(REGEX, line)
    line_to_py_obj = {
        "x": int(match_obj[1]), 
        "y": int(match_obj[2]),
        "pitch": float(match_obj[3]),
        "yaw": float(match_obj[4])
    }
    line_to_json = json.dumps(line_to_py_obj)
    return line_to_json

def MapFileLines(file, mapper):
    arr = []
    for line in file:
        arr.append(mapper(line))
    return arr

controller_commands = MapFileLines(INPUT_FILE, LineToCatoptricControllerCommands)
print(controller_commands)

for command in controller_commands:
    OUTPUT_FILE.write(command[0])
    OUTPUT_FILE.write("\n")
    OUTPUT_FILE.write(command[1])
OUTPUT_FILE.close()







# Miscellanious Notes
#arduino = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75435353934351E01131-if00', baudrate=9600)

# Export Config File Info:
# (x,y) : Pitch=... Yaw=... Roll=...
# Interpreting these values: [CHECK THIS IS WHAT ITS PARSING INTO THE JSON]
# Pitch in rotator is rotation along +- x
# Roll in rotator is rotation along +- y

# Packet format: start, key, x, y, motor, direction, steps
#       direction is 0 backwards, 1 forwards
#       motor documentation gives 11.25 deg/ 16.128 steps ratio


# def LineToArduinoCommands(line):
#     print(LineToJSON(line))
#     # Note: One line of a Config.txt file maps to two command packets
#     # As one command moves it L-R, and another moves it U-D

#     match_obj = re.match(REGEX, line)

#     packet = bytearray([0x21, 0x41]) # start, key

#     packet.append(int(match_obj[1]))
#     packet.append(int(match_obj[2]))

#     print(packet)
    
#     hpacket = packet.copy() # packet issuing the horizontal motion command
#     vpacket = packet.copy() # packet issuing the vertical motion command

#     # No idea what to do for direction, steps high, steps low. Is there a formula?
#     # I think direction is either horizontal or vertical (WHAT VALUES ARE THESE?), then we convert degrees into steps.

#     v_direction = (0, 1) [(float(match_obj[3]) < 0)] # scuffed ternary operator by indexing
#     h_direction = (0, 1) [(float(match_obj[4]) < 0)]

#     #vpacket.append(v_direction)
#     #hpacket.append(h_direction)



#     return (hpacket, vpacket)