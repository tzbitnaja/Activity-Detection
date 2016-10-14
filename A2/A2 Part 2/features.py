# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 13:08:49 2016

@author: cs390mb

This file is used for extracting features over windows of tri-axial accelerometer 
data. We recommend using helper functions like _compute_mean_features(window) to 
extract individual features.

As a side note, the underscore at the beginning of a function is a Python 
convention indicating that the function has private access (although in reality 
it is still publicly accessible).

"""

import numpy as np

def _compute_mean_features(window):
    """
    Computes the mean x, y and z acceleration over the given window. 
    """
    return np.mean(window, axis=0)

def _compute_fft_features(window):

    # we make it calculate the fft along each column which represents x,y,z respectively
    #then we cast it to a float, and take a 3x3 slice of it.

   complex = np.fft.rfft(window,axis=0)
   float_arr = complex.astype(float)

   return float_arr[:3].flatten(order='F')

def _compute_mean_magnitude_features(window):

    #magnitude = np.sqrt(np.sum(np.square(window,axis=0)))
    magnitudes = []
    for row in range(1,window.shape[0]+1):
        magnitudes = np.append(magnitudes,np.sqrt(np.sum(np.square(window[:row]))))

    
    return np.mean(magnitudes)


def extract_features(window):
    """
    Here is where you will extract your features from the data over 
    the given window. We have given you an example of computing 
    the mean and appending it to the feature matrix X.
    
    Make sure that X is an N x d matrix, where N is the number 
    of data points and d is the number of features.
    
    """
    
    x = []
    
    x = np.append(x, _compute_mean_features(window))
    x = np.append(x,_compute_fft_features(window))
    x = np.append(x,_compute_mean_magnitude_features(window))

    return x
