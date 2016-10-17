# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 16:02:58 2016

@author: cs390mb

Assignment 2 : Activity Recognition

This is the starter script used to train an activity recognition 
classifier on accelerometer data.

See the assignment details for instructions. Basically you will train 
a decision tree classifier and vary its parameters and evalute its 
performance by computing the average accuracy, precision and recall 
metrics over 10-fold cross-validation. You will then train another 
classifier for comparison.

Once you get to part 4 of the assignment, where you will collect your 
own data, change the filename to reference the file containing the 
data you collected. Then retrain the classifier and choose the best 
classifier to save to disk. This will be used in your final system.

Make sure to check the assignment details, since the instructions here are
not complete.

"""
import pdb as pdb
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import svm
from features import extract_features # make sure features.py is in the same directory
from util import slidingWindow, reorient, reset_vars
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn import metrics, neighbors
import pickle
#pdb.set_trace()

# %%---------------------------------------------------------------------------
#
#		                 Load Data From Disk
#
# -----------------------------------------------------------------------------

print("Loading data...")
sys.stdout.flush()
data_file = os.path.join('data', 'sample-data.csv')
data = np.genfromtxt(data_file, delimiter=',')
print("Loaded {} raw labelled activity data samples.".format(len(data)))
sys.stdout.flush()

# %%---------------------------------------------------------------------------
#
#		                    Pre-processing
#
# -----------------------------------------------------------------------------

print("Reorienting accelerometer data...")
sys.stdout.flush()
reset_vars()
reoriented = np.asarray([reorient(data[i,1], data[i,2], data[i,3]) for i in range(len(data))])
reoriented_data_with_timestamps = np.append(data[:,0:1],reoriented,axis=1)
data = np.append(reoriented_data_with_timestamps, data[:,-1:], axis=1)


# %%---------------------------------------------------------------------------
#
#		                Extract Features & Labels
#
# -----------------------------------------------------------------------------

# you may want to play around with the window and step sizes
window_size = 20
step_size = 20

# sampling rate for the sample data should be about 25 Hz; take a brief window to confirm this
n_samples = 1000
time_elapsed_seconds = (data[n_samples,0] - data[0,0]) / 1000
sampling_rate = n_samples / time_elapsed_seconds

feature_names = ["mean X", "mean Y", "mean Z","fft X1","fft X2", "fft X3","fft Y1","fft Y2", "fft Y3","fft Z1","fft Z2", "fft Z3", "magnitude_mean"]
class_names = ["Stationary", "Walking"]

print("Extracting features and labels for window size {} and step size {}...".format(window_size, step_size))
sys.stdout.flush()

n_features = len(feature_names)

X = np.zeros((0,n_features))
y = np.zeros(0,)

for i,window_with_timestamp_and_label in slidingWindow(data, window_size, step_size):
    # omit timestamp and label from accelerometer window for feature extraction:
    window = window_with_timestamp_and_label[:,1:-1]  
    # extract features over window:
    x = extract_features(window)
    # append features:
    X = np.append(X, np.reshape(x, (1,-1)), axis=0)
    # append label:
    y = np.append(y, window_with_timestamp_and_label[10, -1])
    
print("Finished feature extraction over {} windows".format(len(X)))
print("Unique labels found: {}".format(set(y)))
sys.stdout.flush()

# %%---------------------------------------------------------------------------
#
#		                    Plot data points
#
# -----------------------------------------------------------------------------

# We provided you with an example of plotting two features.
# We plotted the mean X acceleration against the mean Y acceleration.
# It should be clear from the plot that these two features are alone very uninformative.
print("Plotting data points...")
sys.stdout.flush()
plt.figure(1)
formats = ['bo', 'go']
formats2 = ['b^','r^']
formats3 = ['bs','rs']
for i in range(0,len(y),10): # only plot 1/10th of the points, it's a lot of data!
#    plt.plot(X[i,0], X[i,1], formats[int(y[i])],X[i,3],X[i,6],formats2[int(y[i])],X[i,0],X[i,10],formats3[int(y[i])])
    plt.subplot(221)
    plt.plot(X[i,0], X[i,1], formats[int(y[i])])
    plt.title('Mean')
    
    plt.subplot(222)
    plt.plot(X[i,3],X[i,6], formats2[int(y[i])])
    plt.title('FFT X1vsY1')
    
    plt.subplot(223)
    plt.plot(X[i,0],X[i,10], formats3[int(y[i])])
    plt.title('mean vs Mag_mean')
plt.show()


# %%---------------------------------------------------------------------------
#
#		                Train & Evaluate Classifier
#
# -----------------------------------------------------------------------------

n = len(y)
n_classes = len(class_names)

# TODO: Train and evaluate your decision tree classifier over 10-fold CV.
# Report average accuracy, precision and recall metrics.
tree = DecisionTreeClassifier(criterion="entropy", max_depth=7, max_features = n_features)
cv = cross_validation.KFold(n, n_folds=10, shuffle=False, random_state=None)
true_total = 0
false_total = 0
total = 0

precision = np.full(n_classes, 0.0)
recall = np.full(n_classes, 0.0)

for i, (train_indexes, test_indexes) in enumerate(cv):
    X_train = X[train_indexes, :]
    y_train = y[train_indexes]
    X_test = X[test_indexes, :]
    y_test = y[test_indexes]
    
    tree.fit(X_train, y_train)
    y_pred = tree.predict(X_test)
    
    conf = confusion_matrix(y_test, y_pred)

    print("Fold {}".format(i))

    for i in range(0, n_classes):
        row = conf[i]

        tp_fp = 0.0
        tp_fn = 0.0

        for j in range(0, n_classes):
            tp_fp += conf[j][i]
            tp_fn += conf[i][j]

        if tp_fp != 0:
            precision[i] += row[i]/tp_fp

        if tp_fn != 0:
            recall[i] += row[i]/tp_fn

        true_total += row[i]
        false_total += sum(row) - row[i]
        total += sum(row)

accuracy = float(true_total)/total
for i in range(0, n_classes):
    precision[i] = float(precision[i] / 10.0)
    recall[i] = float(recall[i] /10.0)

treeAcc = accuracy

print "average accuracy over 10 folds: {}".format(accuracy)
print 

for i in range(0, n_classes):
    print"average precision for classifier %d over 10 folds: %f" %(i, precision[i])
    print"average recall for classifier %d over 10 folds: %f" %(i, recall[i])
    print


# TODO: Evaluate another classifier, i.e. SVM, Logistic Regression, k-NN, etc.

clf = neighbors.KNeighborsClassifier(n_neighbors = 2, weights="distance")
true_total = 0
false_total = 0
total = 0

precision = np.full(n_classes, 0.0)
recall = np.full(n_classes, 0.0)

for i, (train_indexes, test_indexes) in enumerate(cv):
    X_train = X[train_indexes, :]
    y_train = y[train_indexes]
    X_test = X[test_indexes, :]
    y_test = y[test_indexes]
    
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    conf = confusion_matrix(y_test, y_pred)

    print("Fold {}".format(i))

    for i in range(0, n_classes):
        row = conf[i]

        tp_fp = 0.0
        tp_fn = 0.0

        for j in range(0, n_classes):
            tp_fp += conf[j][i]
            tp_fn += conf[i][j]

        if tp_fp != 0:
            precision[i] += row[i]/tp_fp

        if tp_fn != 0:
            recall[i] += row[i]/tp_fn

        true_total += row[i]
        false_total += sum(row) - row[i]
        total += sum(row)

accuracy = float(true_total)/total
for i in range(0, n_classes):
    precision[i] = float(precision[i] / 10.0)
    recall[i] = float(recall[i] /10.0)

clfAcc = accuracy

print "average accuracy over 10 folds: {}".format(accuracy)
print 

for i in range(0, n_classes):
    print"average precision for classifier %d over 10 folds: %f" %(i, precision[i])
    print"average recall for classifier %d over 10 folds: %f" %(i, recall[i])
    print
# TODO: Once you have collected data, train your best model on the entire
# dataset. Then save it to disk as follows:

# when ready, set this to the best model you found, trained on all the data:
if treeAcc > clfAcc:
    tree.fit(X, y)
    best_classifier = tree
else:
    clf.fit(X, y)
    best_classifier = clf

with open('classifier.pickle', 'wb') as f: # 'wb' stands for 'write bytes'
    pickle.dump(best_classifier, f)

export_graphviz(tree, out_file='tree10.dot', feature_names = feature_names)
