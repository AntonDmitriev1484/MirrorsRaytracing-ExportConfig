import os
import json
import re
import sys
#import numpy # <- can't install numpy because pip isn't working, they suggest I reinstall Python :(
#import serial

# Constants

pair_system_name = sys.argv[1] # Command line argument specifies what config file we want to use
regex = "\((\d)\,(\d)\) : P=(-?\d{1,4}\.\d{1,6}) Y=(-?\d{1,4}\.\d{1,6}) R=(-?\d{1,4}\.\d{1,6})"
path = ""
file = open("../ConfigExportOutput/"+pair_system_name+"Config.txt","r")

#arduino = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75435353934351E01131-if00', baudrate=9600)
# DO I NEED TO CHANGE THIS FOR MY OWN COMPUTER???? ^^^^^^^^

# Export Config File Info:
# (x,y) : Pitch=... Yaw=... Roll=...
# Interpreting these values: [CHECK THIS IS WHAT ITS PARSING INTO THE JSON]
# Pitch in rotator is rotation along +- x
# Roll in rotator is rotation along +- y

# Arduino Protocol Info:
# Start = 0x21 (!), End = 0x23 (#)
# Key (for motor movement) = 0x41 (A)
# Ack = 0x61 (a), Nack = 0x62 (b)

# Note: NOT WRITING DIRECTLY TO ARDUINO
# Packet format: start, key, x, y, motor, direction, steps
#       direction is 0 backwards, 1 forwards
#       motor documentation gives 11.25 deg/ 16.128 steps ratio

# Ack format: start, ack, key, x, y, motor, end
# Nack format: start, nack, <message> (variable length), end

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

def SendLineToArduino(line):
    commands = LineToArduinoCommands(line)
    # Send out the command here
    # arduino.write(commands[0])
    # arduino.write(commands[1])
    # Control flow to deal with ack / nack
    return commands

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


# json_objects = MapFileLines(file, LineToJSON)
# print(json_objects)

# file.seek(0) # Reset file pointer to top

arduino_commands = MapFileLines(file, LineToArduinoCommands)
print(arduino_commands)

















#print(json_objects)




    # Ultimately, really doesn't matter, because they're unsigned anyways!
    # packet_arr.append(int(match_obj[1]).to_bytes(8,'big')) # x
    # print(int(match_obj[1]).to_bytes(8,'big'))
    # packet_arr.append(int(match_obj[2]).to_bytes(8,'big')) # y