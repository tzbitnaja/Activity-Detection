# My-Activities --enhanced

We are using accelerometer, gyroscope, and heart rate data to train the classifier and to predict activities.

A BandSensorReading class was added to the Android code in order to bundle sensor data from MS Band 2. In the msband service we send the filtered data by create a band reading. (with an optional label)
In the activities tab of the app we added a visualization pie chart whose sections shrink and grow based on the type of activity you’re doing.
So in the Android code files that have been added or modified are band service, exercise fragment, and band reading
 
On the python side there are four scripts that deal with collecting, training, and recognizing data and a feature extraction python script.
