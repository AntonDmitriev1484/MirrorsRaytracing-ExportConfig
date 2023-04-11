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

pair_system_name = sys.argv[1] # Command line argument specifies what config file we want to use
regex = "\((\d)\,(\d)\) : P=(-?\d{1,4}\.\d{1,6}) Y=(-?\d{1,4}\.\d{1,6}) R=(-?\d{1,4}\.\d{1,6})"
path = ""
file = open("../ConfigExportOutput/"+pair_system_name+"Config.txt","r")

#arduino = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75435353934351E01131-if00', baudrate=9600)

# Export Config File Info:
# (x,y) : Pitch=... Yaw=... Roll=...
# Interpreting these values: [CHECK THIS IS WHAT ITS PARSING INTO THE JSON]
# Pitch in rotator is rotation along +- x
# Roll in rotator is rotation along +- y

# Packet format: start, key, x, y, motor, direction, steps
#       direction is 0 backwards, 1 forwards
#       motor documentation gives 11.25 deg/ 16.128 steps ratio

def LineToArduinoCommands(line):
    print(LineToJSON(line))
    # Note: One line of a Config.txt file maps to two command packets
    # As one command moves it L-R, and another moves it U-D

    match_obj = re.match(regex, line)

    packet = bytearray([0x21, 0x41]) # start, key

    packet.append(int(match_obj[1]))
    packet.append(int(match_obj[2]))

    print(packet)
    
    hpacket = packet.copy() # packet issuing the horizontal motion command
    vpacket = packet.copy() # packet issuing the vertical motion command

    # No idea what to do for direction, steps high, steps low. Is there a formula?
    # I think direction is either horizontal or vertical (WHAT VALUES ARE THESE?), then we convert degrees into steps.

    v_direction = (0, 1) [(float(match_obj[3]) < 0)] # scuffed ternary operator by indexing
    h_direction = (0, 1) [(float(match_obj[5]) < 0)]

    #vpacket.append(v_direction)
    #hpacket.append(h_direction)



    return (hpacket, vpacket)

def LineToCatoptricControllerCommands(line):
    print(LineToArduinoCommands(line))

    match_obj = re.match(regex, line)

    x = int(match_obj[1])
    y = int(match_obj[2])

    v_direction = (0, 1) [(float(match_obj[3]) < 0)] # scuffed ternary operator by indexing
    h_direction = (0, 1) [(float(match_obj[5]) < 0)]

    # Still need to add 'step' field
    # Also I think I need to re-do how I do my rotation translation again :(

    # move row col motor direction steps
    ud_motor_command = 'move {y} {x} 1 {y_direction}'
    lr_motor_command = 'move {y} {x} 0 {h_direction}'


    return (lr_motor_command, ud_motor_command)


def LineToJSON(line):
    match_obj = re.match(regex, line)
    line_to_py_obj = {
        "x": int(match_obj[1]), 
        "y": int(match_obj[2]),
        "vertical_change": float(match_obj[3]),
        "horizontal_change": float(match_obj[5])
    }
    line_to_json = json.dumps(line_to_py_obj)
    return line_to_json

def MapFileLines(file, mapper):
    arr = []
    for line in file:
        arr.append(mapper(line))
    return arr



controller_commands = MapFileLines(file, LineToCatoptricControllerCommands)
print(controller_commands)


new_file = open("CatoptricInput.txt", "a")
for command in controller_commands:
    new_file.write(command)
new_file.close()
















#print(json_objects)




    # Ultimately, really doesn't matter, because they're unsigned anyways!
    # packet_arr.append(int(match_obj[1]).to_bytes(8,'big')) # x
    # print(int(match_obj[1]).to_bytes(8,'big'))
    # packet_arr.append(int(match_obj[2]).to_bytes(8,'big')) # y