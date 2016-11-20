package cs.umass.edu.myactivitiestoolkit.steps;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.util.Log;

import java.sql.Time;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import cs.umass.edu.myactivitiestoolkit.constants.Constants;
import cs.umass.edu.myactivitiestoolkit.processing.Filter;

/**
 * This class is responsible for detecting steps from the accelerometer sensor.
 * All {@link OnStepListener step listeners} that have been registered will
 * be notified when a step is detected.
 */
public class StepDetector implements SensorEventListener {
    /**
     * Used for debugging purposes.
     */
    @SuppressWarnings("unused")
    private static final String TAG = StepDetector.class.getName();

    /**
     * Maintains the set of listeners registered to handle step events.
     **/
    private ArrayList<OnStepListener> mStepListeners;
    private Filter filter = new Filter(2);
    private LinkedList<Float []> buffer = new LinkedList<>();
    private double window = 1000000 * 1000;
    private long lastStepped = 0;
    private int bufferCounter = 0;
    final private int maxBufferCount = 30;
    float minX, minY, minZ, maxX, maxY, maxZ;
    private float dynThreshold;
    private float lastWindowVal;
    private boolean buffAccuFirstTime = false;
    private boolean x,y,z;


    /**
     * The number of steps taken.
     */
    private int stepCount;

    public StepDetector() {
        mStepListeners = new ArrayList<>();
        stepCount = 0;
        minX = minY = minZ = maxX = maxY = maxZ = 0;
        x=y=z=false;
    }

    /**
     * Registers a step listener for handling step events.
     *
     * @param stepListener defines how step events are handled.
     */
    public void registerOnStepListener(final OnStepListener stepListener) {
        mStepListeners.add(stepListener);
    }

    /**
     * Unregisters the specified step listener.
     *
     * @param stepListener the listener to be unregistered. It must already be registered.
     */
    public void unregisterOnStepListener(final OnStepListener stepListener) {
        mStepListeners.remove(stepListener);
    }

    /**
     * Unregisters all step listeners.
     */
    public void unregisterOnStepListeners() {
        mStepListeners.clear();
    }

    /**
     * Here is where you will receive accelerometer readings, buffer them if necessary
     * and run your step detection algorithm. When a step is detected, call
     * {@link #onStepDetected(long, float[])} to notify all listeners.
     * <p>
     * Recall that human steps tend to take anywhere between 0.5 and 2 seconds.
     *
     * @param event sensor reading
     */
    @Override
    public void onSensorChanged(SensorEvent event) {

        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {


            float[] fv = filter.getFilteredValues(event.values);
            Float[] nFv = new Float[fv.length];
            for(int i=0; i<fv.length; i++){
                nFv[i] = fv[i];
            }

            buffer.add(nFv);
            bufferCounter++;
            if(bufferCounter == maxBufferCount){
                bufferCounter = 0;
                buffAccuFirstTime = true;

                for (Float[] e : buffer) {
                    if (minX > e[0]) {
                        minX = e[0];
                    }
                    if (maxX < e[0]) {
                        maxX = e[0];
                    }
                    if (minY > e[1]) {
                        minY = e[1];
                    }
                    if (maxY < e[1]) {
                        maxY = e[1];
                    }
                    if (minZ > e[2]) {
                        minZ = e[2];
                    }
                    if (maxZ < e[2]) {
                        maxZ = e[2];
                    }
                }

                if (maxX > maxY && maxX > maxZ) {
                    dynThreshold = (minX+maxX)/2;
                    lastWindowVal = buffer.getLast()[0];
                    x=true; y=z=false;

                } else if (maxY > maxZ) {
                    dynThreshold = (minY+ maxY)/2;
                    lastWindowVal = buffer.getLast()[1];
                    y=true; x=z=false;
                } else {
                    dynThreshold = (minZ+maxZ)/2;
                    lastWindowVal = buffer.getLast()[2];
                    z=true; x=y=false;
                }
                maxX = maxY = maxZ = minX = minY = minZ = 0;
                buffer.clear();
                return ;

            }
            if(buffAccuFirstTime){
                Float value;
                if(x){
                    value = fv[0];
                } else if(y){
                    value = fv[1];
                } else {
                    value = fv[2];
                }

                if((value < dynThreshold) && (lastWindowVal > dynThreshold)){
                    Log.i(TAG, "In Treshold");
                    long curTimeStamp = (long) ((double) event.timestamp / Constants.TIMESTAMPS.NANOSECONDS_PER_MILLISECOND);
                    if(event.timestamp-lastStepped >= window) {
                        Log.i(TAG, "Window: " +  window);
                        onStepDetected(curTimeStamp, event.values);
                        lastStepped = event.timestamp;
                    }
                }
                lastWindowVal = value;
            }

        }
    }





    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {
        // do nothing
    }



    /**
     * This method is called when a step is detected. It updates the current step count,
     * notifies all listeners that a step has occurred and also notifies all listeners
     * of the current step count.
     */
    private void onStepDetected(long timestamp, float[] values) {
        stepCount++;
        for (OnStepListener stepListener : mStepListeners) {
            stepListener.onStepDetected(timestamp, values);
            stepListener.onStepCountUpdated(stepCount);
        }
    }
}