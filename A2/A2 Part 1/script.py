# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:40:38 2016

@author: cs390mb

Assignment A2 : Activity Recognition
Part 1 : Supervised Classification

This script generates noisy average and maximum speed data for 
walking, running and biking and plots the datapoints along with 
the decision boundary of a trained Suport Vector Machine (SVM) 
classifier.

Note that this data is generated using means and standard deviations that 
are not entirely realistic. When you collect actual data, you will likely 
find that it is not as clean, i.e. there is more class overlap and therefore 
more ambiguity.

Run this script to visualize the generated data, each data point colored 
according to the corresponding activity. Change the variable n_samples 
to be much smaller (~10 samples) and much larger (> 1000 samples) and 
see how the decision boundaries change.

Refer to the assignment details on what you need to do here.

"""

# %%---------------------------------------------------------------------------
#
#		                          Imports
#
# -----------------------------------------------------------------------------
import pdb as pdb
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.metrics import confusion_matrix
from sklearn import cross_validation

pdb.set_trace()

# %%---------------------------------------------------------------------------
#
#		                      Initialization
#
# -----------------------------------------------------------------------------

n_samples = 100 # number of data points per activity
n_dim = 2 # number of feature dimensions; 2 for this example so that we can visualize

# for each activity, we specify the expected max, expected average and the standard deviation  
# for simplicity the stddev is the same for both the max and average features.
stats = {'walking' : {'expected_max' : 7.0, 'expected_average' : 3.1, 'stddev' : 1.25, 'samples' : [], 'format' : 'ro'}, 
         'running' : {'expected_max' : 10.5, 'expected_average' : 5.25, 'stddev' : 2.5, 'samples' : [], 'format' : 'go'},
         'biking' : {'expected_max' : 17.0, 'expected_average' : 9.25, 'stddev' : 16.0, 'samples' : [], 'format' : 'bo'}}

plt.figure() # always call plt.figure() unless you want to plot points on an existing plot
plt_handles = [] # handles to the plots, used to configure the legend

X = np.zeros((n_samples * len(stats), n_dim))
y = np.zeros((n_samples * len(stats),), dtype=int)

# %%---------------------------------------------------------------------------
#
#		      Generate data by sampling a normal distribution
#
# -----------------------------------------------------------------------------

for index, (activity, values) in enumerate(stats.items()):
    print("The average speed for {} is {} mph.".format(activity, values['expected_average']))
    # the samples are taken from a normal distribution centered around [expected max, expected average]
    values['samples'] = np.asarray([np.random.multivariate_normal([values['expected_max'], values['expected_average']], values['stddev'] * np.eye(2)) for _ in range(n_samples)])
    # plot the data samples
    h, = plt.plot(values['samples'][:,0], values['samples'][:,1], values['format'], label=activity)
    plt_handles.append(h)
    # append features:
    X[(index*n_samples):((index+1)*n_samples),:] = values['samples']
    # append labels:
    y[(index*n_samples):((index+1)*n_samples)] = [index] * n_samples

# %%---------------------------------------------------------------------------
#
#		          Train Support Vector Machine Classifier
#
# -----------------------------------------------------------------------------

n = len(y)

# SVM regularization parameter : For the purpose of this assignment, we will 
# just set it to 1.0; in real applications, you should choose the C that 
# gives the best performance metrics on a validation dataset, a separate 
# dataset in addition to training/test. You don't need to do this.
C = 1.0  

clf = svm.SVC(kernel = 'linear', C=C )

cv = cross_validation.KFold(n, n_folds=10, shuffle=False, random_state=None)
tnc = 0
ttruths = 0
tfalse = 0

avgacc = 0.0
avgprecisionA = 0.0
avgprecisionB = 0.0
avgprecisionC = 0.0
avgrecallA = 0.0
avgrecallB = 0.0
avgrecallC = 0.0

for i, (train_indexes, test_indexes) in enumerate(cv):
    X_train = X[train_indexes, :]
    y_train = y[train_indexes]
    X_test = X[test_indexes, :]
    y_test = y[test_indexes]
    clf.fit(X_train, y_train)

    laccuracy = 0.0

    percisionA = 0.0
    percisionB = 0.0
    percisionC = 0.0
    recallA = 0.0
    recallB = 0.0
    recallC = 0.0

    # predict the labels on the test data
    y_pred = clf.predict(X_test)

    # show the comparison between the predicted and ground-truth labels
    conf = confusion_matrix(y_test, y_pred, labels=[0,1,2])
    
    print("Fold {} : The confusion matrix is :".format(i))
    print conf
    
    # TODO: Compute the accuracy, precision and recall from the confusion matrix
    firstRow = conf[0]
    secondRow = conf[1]
    thirdRow = conf[2]

    truths = firstRow[0]+secondRow[1]+thirdRow[2]
    false = firstRow[1]+firstRow[2]+secondRow[0]+secondRow[2]+thirdRow[0]+thirdRow[1]

    #Percision calculations
    if((firstRow[0]+secondRow[0]+thirdRow[0]) != 0):
        percisionA = float(firstRow[0]) / (firstRow[0]+secondRow[0]+thirdRow[0])
    else:
        percisionA = 0.0
    if((secondRow[1]+firstRow[1]+thirdRow[1])!= 0 ):
        percisionB = float(secondRow[1]) / (firstRow[1] + secondRow[1] + thirdRow[1])
    else:
        percisionB = 0.0

    if(firstRow[2]+secondRow[2]+thirdRow[2] != 0):
        percisionC = float(thirdRow[2]) / (firstRow[2] + secondRow[2] + thirdRow[2])
    else:
        percisionC = 0.0

    #Recall calculations
    if(sum(firstRow)!=0):
        recallA = float(firstRow[0]) / sum(firstRow)
    else:
        recallA = 0.0
    if(sum(secondRow)):
        recallB = float(secondRow[1]) / sum(secondRow)
    else:
        recallB = 0.0
    if(sum(thirdRow)!=0):
        recallC = float(thirdRow[2]) / sum(thirdRow)
    else:
        recallC = 0.0
    #localAcuracyCalcs
    laccuracy = float(truths)/(truths+false)

    #ForGlobalAccuracy
    tnc +=truths+false
    ttruths+= truths
    tfalse += false

    avgprecisionA += percisionA
    avgprecisionB += percisionB
    avgprecisionC += percisionC
    avgrecallA += recallA
    avgrecallB += recallB
    avgrecallC += recallC

    print "accuracy: {}".format(laccuracy)
    print "percision for classifier A: %.2f" % percisionA
    print "percision for classifier B: %.2f" % percisionB
    print "percision for classifier C: %.2f" % percisionC
    print "recall for classifier A: %.2f" %recallA
    print "recall for classifier B: %.2f" % recallB
    print "recall for classifier C: %.2f" % recallC


    
    print("\n")

# TODO: Output the average accuracy, precision and recall over the 10 folds
avgacc = float(ttruths)/tnc
avgprecisionA /= 10.0
avgprecisionB /= 10.0
avgprecisionC /= 10.0
avgrecallA /= 10.0
avgrecallB /= 10.0
avgrecallC /= 10.0

print "average accuracy over 10 folds: {}".format(avgacc)
print "average percision for classifier A over 10 folds: {}".format(avgprecisionA)
print "average percision for classifier B over 10 folds: {}".format(avgprecisionB)
print "average percision for classifier C over 10 folds: {}".format(avgprecisionC)
print "average recall for classifier A over 10 folds: {}".format(avgrecallA)
print "average recall for classifier B over 10 folds: {}".format(avgrecallB)
print "average recall for classifier C over 10 folds: {}".format(avgrecallC)

# TOO: Then change the CV parameter shuffle to True and describe how the results change.
#----------- Answer---------------------------------------------------------------------
# The results change that rather than one diagonal having the majority fo the correctness
# the correct results and the right resutls get more spread out. I.E it's able to classify other things better
# while also gaining a higher degree in error. But more things are classified

# Train on entire dataset; that will give us the decision boundary we'll plot.
clf.fit(X, y)

# %%---------------------------------------------------------------------------
#
#		                 Plot Decision Boundaries
#
# -----------------------------------------------------------------------------

xx = np.linspace(0, 30)

# Decision boundary for walking and biking (we won't plot this one)

w = clf.coef_[0] #+ clf.coef_[1]
a = -w[0] / w[1]
yy = a * xx - (clf.intercept_[0]) / w[1]

# Plot decision boundary for walking and running

w = clf.coef_[1] #+ clf.coef_[1]
a = -w[0] / w[1]
yy = a * xx - (clf.intercept_[1]) / w[1]

plt.plot(xx, yy, 'k-')

# Plot decision boundary for running and biking

w = clf.coef_[2]
a = -w[0] / w[1]
yy = a * xx - (clf.intercept_[2]) / w[1]

plt.plot(xx, yy, 'k-')

# %%---------------------------------------------------------------------------
#
#		                   Format and Show Plot
#
# -----------------------------------------------------------------------------

plt.xlabel('max speed (mph)')
plt.ylabel('average speed (mph)')
plt.title('Average and max speed data samples for various activities')
plt.legend(handles = plt_handles)
plt.show()
# call plt.savefig(filename) to save to disk
