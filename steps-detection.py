# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:34:11 2016

Assignment A1 : Step Detection

@author: cs390mb

This Python script receives incoming accelerometer data through the 
server, detects step events and sends them back to the server for 
visualization/notifications.

Refer to the assignment details at ... For a beginner's 
tutorial on coding in Python, see goo.gl/aZNg0q.

"""

import socket
import sys
import json
import threading
import numpy as np

# TODO: Replace the string with your user ID
user_id = "9f.34.54.4f.9a.b1.70.40.c6.30"
window = 1000
lastStep = 0.0
maxX = minX = maxY = minY = maxZ = minZ = 0.0
threshold = 0.0

prevVal = 0.0
currVal = 0.0
curr = []
temp = []

enoughBuffered = False
x=y=z = False

buffer = [0]*30
bufferCount = 0
count = 0

'''
    This socket is used to send data back through the data collection server.
    It is used to complete the authentication. It may also be used to send 
    data or notifications back to the phone, but we will not be using that 
    functionality in this assignment.
'''
send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_socket.connect(("none.cs.umass.edu", 9999))

def onStepDetected(timestamp):
    """
    Notifies the client that a step has been detected.
    """
    send_socket.send(json.dumps({'user_id' : user_id, 'sensor_type' : 'SENSOR_SERVER_MESSAGE', 'message' : 'STEP_DETECTED', 'data': {'timestamp' : timestamp}}) + "\n")

def detectSteps(timestamp, filteredValues):
    """
    Accelerometer-based step detection algorithm.
    
    In assignment A1, you will implement your step detection algorithm. 
    This may be functionally equivalent to your Java step detection 
    algorithm if you like. Remember to use the global keyword if you 
    would like to access global variables such as counters or buffers. 
    When a step has been detected, call the onStepDetected method, passing  
    in the timestamp.
    """
    global window
    global lastStep
    global maxX, maxY, maxZ, minX, minY, minZ
    global threshold
    global prevVal
    global currVal
     
    global enoughBuffered
    global x, y, z
    global stepCount
    
    global buffer
    global bufferCount
    
    global temp
    global curr
    global count
    # TODO: Step detection algorithm
    
    buffer.insert(bufferCount, filteredValues)
    bufferCount = bufferCount + 1
    
    if (bufferCount == 30):
        bufferCount = 0
        enoughBuffered = True
        
        for value in range (0, 30):
            curr = buffer[value]
            if (maxX < curr[0]):
                maxX = curr[0]
            elif (minX > curr[0]):
                minX = curr[0]
            if (maxY < curr[1]):
                maxY = curr[1]
            elif (minY > curr[1]):
                minY = curr[1]
            if (maxZ < curr[2]):
                maxZ = curr[2]
            elif (minZ > curr[2]):
                minZ = curr[2]
                
        temp = buffer[29]
        if (maxX > maxY) & (maxX > maxZ):
            threshold = (maxX + minX)/2
            prevVal = temp[0]
            x = True
            y = False
            z = False
        elif maxY > maxZ:
            threshold = (maxY + minY)/2
            prevVal = temp[1]
            x = False
            y = True
            z = False
        else:
            threshold = (maxZ + minZ)/2
            prevVal = temp[2]
            x = False
            y = False
            z = True
        maxX = maxY = maxZ = minX = minY = minZ = 0
        return
    
    if enoughBuffered == True:
        if (x == True):
            currVal = filteredValues[0]
        elif (y == True):
            currVal = filteredValues[1]
        else:
            currVal = filteredValues[2]
            
        if (currVal < threshold) & (prevVal > threshold):
            print("here")
            count  = count + 1
            if (timestamp - lastStep) >= window:
                onStepDetected(timestamp)
                lastStep = timestamp
        prevVal = currVal
    
           
    return
    
    

#################   Server Connection Code  ####################

'''
    This socket is used to receive data from the data collection server
'''
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receive_socket.connect(("none.cs.umass.edu", 8888))
# ensures that after 1 second, a keyboard interrupt will close
receive_socket.settimeout(1.0)

msg_request_id = "ID"
msg_authenticate = "ID,{}\n"
msg_acknowledge_id = "ACK"

def authenticate(sock):
    """
    Authenticates the user by performing a handshake with the data collection server.
    
    If it fails, it will raise an appropriate exception.
    """
    message = sock.recv(256).strip()
    if (message == msg_request_id):
        print("Received authentication request from the server. Sending authentication credentials...")
        sys.stdout.flush()
    else:
        print("Authentication failed!")
        raise Exception("Expected message {} from server, received {}".format(msg_request_id, message))
    sock.send(msg_authenticate.format(user_id))

    try:
        message = sock.recv(256).strip()
    except:
        print("Authentication failed!")
        raise Exception("Wait timed out. Failed to receive authentication response from server.")
        
    if (message.startswith(msg_acknowledge_id)):
        ack_id = message.split(",")[1]
    else:
        print("Authentication failed!")
        raise Exception("Expected message with prefix '{}' from server, received {}".format(msg_acknowledge_id, message))
    
    if (ack_id == user_id):
        print("Authentication successful.")
        sys.stdout.flush()
    else:
        print("Authentication failed!")
        raise Exception("Authentication failed : Expected user ID '{}' from server, received '{}'".format(user_id, ack_id))


try:
    print("Authenticating user for receiving data...")
    sys.stdout.flush()
    authenticate(receive_socket)
    
    print("Authenticating user for sending data...")
    sys.stdout.flush()
    authenticate(send_socket)
    
    print("Successfully connected to the server! Waiting for incoming data...")
    sys.stdout.flush()
        
    previous_json = ''
        
    while True:
        try:
            message = receive_socket.recv(1024).strip()
            json_strings = message.split("\n")
            json_strings[0] = previous_json + json_strings[0]
            for json_string in json_strings:
                try:
                    data = json.loads(json_string)
                except:
                    previous_json = json_string
                    continue
                previous_json = '' # reset if all were successful
                sensor_type = data['sensor_type']
                if (sensor_type == u"SENSOR_ACCEL"):
                    t=data['data']['t']
                    x=data['data']['x']
                    y=data['data']['y']
                    z=data['data']['z']
                    
                    processThread = threading.Thread(target=detectSteps, args=(t,[x,y,z]))
                    processThread.start()
                
            sys.stdout.flush()
        except KeyboardInterrupt: 
            # occurs when the user presses Ctrl-C
            print("User Interrupt. Quitting...")
            break
        except Exception as e:
            # ignore exceptions, such as parsing the json
            # if a connection timeout occurs, also ignore and try again. Use Ctrl-C to stop
            # but make sure the error is displayed so we know what's going on
            if (e.message != "timed out"):  # ignore timeout exceptions completely       
                print(e)
            pass
except KeyboardInterrupt: 
    # occurs when the user presses Ctrl-C
    print("User Interrupt. Quitting...")
finally:
    print >>sys.stderr, 'closing socket for receiving data'
    receive_socket.shutdown(socket.SHUT_RDWR)
    receive_socket.close()
    
    print >>sys.stderr, 'closing socket for sending data'
    send_socket.shutdown(socket.SHUT_RDWR)
    send_socket.close()