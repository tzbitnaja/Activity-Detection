"""
@author: toma
"""
import os
import sys
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from features import extract_features
from util import slidingWindow, reorient, reset_vars
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
import pickle

# %%---------------------------------------------------------------------------
#
#		                 Load Data From Disk
#
# -----------------------------------------------------------------------------

print("Loading data...")
sys.stdout.flush()
data_file = os.path.join('data', 'my-band-data.csv')
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
#accelerometer data
#reoriented = np.asarray([reorient(data[i,2], data[i,3], data[i,4]) for i in range(len(data))])
#gyroscope data
#reoriented2 = np.asarray([reorient(data[i,5], data[i,6], data[i,7]) for i in range(len(data))])

"""
as per Sean's suggestion, we did not bother reorienting the data
"""

#append accelerometer to timestamps
data_with_timestamps = np.append(data[:,0:1],data[:,2:5],axis=1)
#append gyroscope to data
data_with_timestamps2 = np.append(data_with_timestamps,data[:,5:8],axis=1)
#append heartrate to data
data_with_timestamps3 = np.append(data_with_timestamps2, np.reshape(data[:,-1],(len(data),1)) , axis=1)

#append heart rate
data = np.append(data_with_timestamps3, np.reshape(data[:,1],(len(data),1)), axis=1)


# %%---------------------------------------------------------------------------
#
#		                Extract Features & Labels
#
# -----------------------------------------------------------------------------
#2 sec window size
window_size = 50
step_size = 50

feature_names = ["mean X", "mean Y", "mean Z","fft X","fft Y", "fft Z", "std dev X", "std dev Y", "std dev Z", "magnitude_mean", "mean gX", "mean gY", "mean gZ","fft gX","fft gY", "fft gZ", "std dev gX", "std dev gY", "std dev gZ", "g_magnitude_mean", "heart rate"]
class_names = ["sitting", "running", "boing", "clapping"]

print("Extracting features and labels for window size {} and step size {}...".format(window_size, step_size))
sys.stdout.flush()

n_features = len(feature_names)

X = np.zeros((0, n_features))
aX = np.zeros((0, n_features))
y = np.zeros(0,)

for i,window_with_timestamp_and_label in slidingWindow(data, window_size, step_size):
    # omit timestamp and label from accelerometer window for feature extraction:
    window1 = window_with_timestamp_and_label[:,1:4]
    window2 = window_with_timestamp_and_label[:,4:7]  

    # extract features over window:
    #accel
    x = extract_features(window1) 
    #gyroscope
    gx = extract_features(window2)
    #heart rate is a feature of its own, therefore don't extract

    # append features to array:
    aX = np.reshape(np.append(np.reshape(x, (1,-1)), np.reshape(gx, (1,-1))), (1,-1))
    bX = np.reshape(np.append(aX, window_with_timestamp_and_label[(i-1)%20, -2]), (1,-1))

    X = np.append(X, bX, axis=0)
    y = np.append(y, window_with_timestamp_and_label[10, -1])
    
print("Finished feature extraction over {} windows".format(len(X)))
print("Unique labels found: {}".format(set(y)))
sys.stdout.flush()


n = len(y)
n_classes = len(class_names)

#use tree classifier because it should produce pretty good results
#considering that data cannot be classified using a linear classifier
tree = DecisionTreeClassifier(criterion="entropy")
#use 10 folds
cv = cross_validation.KFold(n, n_folds=10, shuffle=True, random_state=None)
true_total = 0
false_total = 0
total = 0

precision = np.full(n_classes, 0.0)
recall = np.full(n_classes, 0.0)

#train the classifier over the 10 folds
for i, (train_indexes, test_indexes) in enumerate(cv):
    X_train = X[train_indexes, :]
    y_train = y[train_indexes]
    X_test = X[test_indexes, :]
    y_test = y[test_indexes]
    
    tree.fit(X_train, y_train)

    y_pred = tree.predict(X_test)
    
    conf = confusion_matrix(y_test, y_pred)

    print("Fold {}".format(i))

    #calculate precision and recalll
    #by basically counting each row/columns truths and falses
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

tree.fit(X_train, y_train)
treeAcc = accuracy
# Report average accuracy, and also precision and recall metrics for each fold.
print "average accuracy over 10 folds: {}".format(accuracy)
print 

for i in range(0, n_classes):
    print"average precision for classifier %d over 10 folds: %f" %(i, precision[i])
    print"average recall for classifier %d over 10 folds: %f" %(i, recall[i])
    print

with open('classifier.pickle', 'wb') as f: # 'wb' stands for 'write bytes'
    pickle.dump(tree, f)
export_graphviz(tree, out_file='tree.dot', feature_names = feature_names)