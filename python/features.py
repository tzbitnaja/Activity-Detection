# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 13:08:49 2016

@author: toma

"""

import numpy as np

def _compute_mean_features(window):
    """
    Computes the mean x, y and z acceleration over the given window. 
    """

    return np.mean(window, axis=0)

def _compute_fft_features(window):
    """
    compute multi-dimensional fft (fftn) from the window
    and then find the dominant frequency of each column
    """
    sp = np.fft.fftn(window).astype(float)
    freq = np.fft.fftfreq(len(window))
   
    fft = np.array([freq[np.argmax(sp[:,0])], freq[np.argmax(sp[:,1])], freq[np.argmax(sp[:,2])]])

    return fft

def _compute_mean_magnitude_features(window):
    """
    compute mean magnitude
    """
    magnitude = np.sqrt(np.sum(np.square(window)))
    

    return np.mean(magnitude)
    
def _compute_std_dev_features(window):

    return np.std(window, axis=0)

def extract_features(window):
    """
    extract features.
    there are 10 features per window    
    """
    
    x = []
    
    x = np.append(x, _compute_mean_features(window))
    x = np.append(x,_compute_fft_features(window))
    x = np.append(x,_compute_mean_magnitude_features(window))
    x = np.append(x,_compute_std_dev_features(window))

    return x
