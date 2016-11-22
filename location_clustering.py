# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 15:34:11 2016

Assignment A5 : Location Clustering

@author: cs390mb

This Python script clusters location data using k-Means / Mean Shift 
upon request from the client.

"""

import socket
import sys
import json
import numpy as np
from sklearn.cluster import KMeans, MeanShift

# TODO: Replace the string with your user ID
user_id = "9f.34.54.4f.9a.b1.70.40.c6.30aaaaaa"

'''
    This socket is used to send data back through the data collection server.
    It is used to complete the authentication. It may also be used to send 
    data or notifications back to the phone, but we will not be using that 
    functionality in this assignment.
'''
send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
send_socket.connect(("none.cs.umass.edu", 9999))
    
def send_clusters(indexes):
    """
    Notifies the client of cluster indexes
    """
    indexes = list(np.asarray(indexes).astype(str))
    send_socket.send(json.dumps({'user_id' : user_id, 'sensor_type' : 'SENSOR_SERVER_MESSAGE', 'message' : 'CLUSTER', 'indexes' : json.dumps(indexes)}) + "\n")

def cluster(latitudes, longitudes, algorithm, *args):
    """
    Clusters the given locations according to the algorithm specified.
    
    TODO: You should construct a N x 2 matrix of (latitude, longitude) pairs, 
    where N is the number of locations (= len(latitudes) = len(longitudes)).
    
    Then according to the algorithm parameter ("k_means" or "mean_shift"), 
    call the appropriate scikit-learn function. For k-means, k=args[0].
    
    Like classification algorithms, first create an instance of the clustering 
    algorithm object. Then the clustering is done using the fit() 
    function. The indexes of those points are then acquired using the 
    labels_ field.
    
    You can simply pass labels_ as a parameter to send_clusters() and the 
    Android application will receive the cluster indexes.
    
    """
    matrix = []
    for i in range(len(latitudes)):
        matrix.append([latitudes[i], longitudes[i]])
        
    #np.column_stack(([latitudes], [longitudes]))
    
    if algorithm == "mean_shift":
        ms = MeanShift()
        ms.fit(matrix)
        
        ms_labels = ms.labels_
        send_clusters(ms_labels)
    elif algorithm == "k_means":
        km = KMeans(n_clusters=args[0])
        km.fit(matrix)
        
        km_labels = km.labels_
        send_clusters(km_labels)
        
    
    # TODO: Do what the comments / assignment details tell you to do.
    
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
                if (sensor_type == u"SENSOR_CLUSTERING_REQUEST"):
                    t=data['data']['t'] # timestamp isn't used
                    algorithm = data['data']['algorithm']
                    k = data['data']['k']
                    latitudes=data['data']['latitudes']
                    longitudes=data['data']['longitudes']
                    cluster(latitudes, longitudes, algorithm, k)
                
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
            else:
                previous_json=''
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
