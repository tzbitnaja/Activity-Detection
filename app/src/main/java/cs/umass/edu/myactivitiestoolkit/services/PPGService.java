package cs.umass.edu.myactivitiestoolkit.services;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.hardware.Camera;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;
import android.view.Gravity;
import android.view.WindowManager;

import java.util.LinkedList;

import cs.umass.edu.myactivitiestoolkit.R;
import cs.umass.edu.myactivitiestoolkit.ppg.HRSensorReading;
import cs.umass.edu.myactivitiestoolkit.ppg.PPGSensorReading;
import cs.umass.edu.myactivitiestoolkit.constants.Constants;
import cs.umass.edu.myactivitiestoolkit.ppg.HeartRateCameraView;
import cs.umass.edu.myactivitiestoolkit.ppg.PPGEvent;
import cs.umass.edu.myactivitiestoolkit.ppg.PPGListener;
import cs.umass.edu.myactivitiestoolkit.processing.Filter;
import edu.umass.cs.MHLClient.client.MobileIOClient;

/**
 * Photoplethysmography service. This service uses a {@link HeartRateCameraView}
 * to collect PPG data using a standard camera with continuous flash. This is where
 * you will do most of your work for this assignment.
 * <br><br>
 * <b>ASSIGNMENT (PHOTOPLETHYSMOGRAPHY)</b> :
 * In {@link #onSensorChanged(PPGEvent)}, you should smooth the PPG reading using
 * a {@link Filter}. You should send the filtered PPG reading both to the server
 * and to the {@link cs.umass.edu.myactivitiestoolkit.view.fragments.HeartRateFragment}
 * for visualization. Then call your heart rate detection algorithm, buffering the
 * readings if necessary, and send the bpm measurement back to the UI.
 * <br><br>
 * EXTRA CREDIT:
 *      Follow the steps outlined <a href="http://www.marcoaltini.com/blog/heart-rate-variability-using-the-phones-camera">here</a>
 *      to acquire a cleaner PPG signal. For additional extra credit, you may also try computing
 *      the heart rate variability from the heart rate, as they do.
 *
 * @author CS390MB
 *
 * @see HeartRateCameraView
 * @see PPGEvent
 * @see PPGListener
 * @see Filter
 * @see MobileIOClient
 * @see PPGSensorReading
 * @see Service
 */
public class PPGService extends SensorService implements PPGListener

{
    @SuppressWarnings("unused")
    /** used for debugging purposes */
    private static final String TAG = PPGService.class.getName();
    private class SignalRep{
        public SignalRep(double value, long time){
            data=value;
            timestamp = time;
        }

        double data;
        long timestamp;
    }

    /* Surface view responsible for collecting PPG data and displaying the camera preview. */
    private HeartRateCameraView mPPGSensor;
    Filter filter = new Filter(3.83f);
    Filter lowpass = new Filter(2.7f);

    private LinkedList<Double> buffer = new LinkedList<>();
    private LinkedList<Long> timeBuffer = new LinkedList<>();
    private LinkedList<SignalRep> dipBuffer= new LinkedList<>();
    private final long bufferTime = 3000; // bufferTime in milisecond

    @Override
    protected void start() {
        Log.d(TAG, "START");
        mPPGSensor = new HeartRateCameraView(getApplicationContext(), null);

        WindowManager winMan = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
        WindowManager.LayoutParams params = new WindowManager.LayoutParams(WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_SYSTEM_ALERT,
                WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH |
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                        WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL |
                        WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                        WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
                PixelFormat.TRANSLUCENT);

        //surface view dimensions and position specified where service intent is called
        params.gravity = Gravity.TOP | Gravity.START;
        params.x = 0;
        params.y = 0;

        //display the surface view as a stand-alone window
        winMan.addView(mPPGSensor, params);
        mPPGSensor.setZOrderOnTop(true);

        // only once the surface has been created can we start the PPG sensor
        mPPGSensor.setSurfaceCreatedCallback(new HeartRateCameraView.SurfaceCreatedCallback() {
            @Override
            public void onSurfaceCreated() {
                mPPGSensor.start(); //start recording PPG
            }
        });

        super.start();
    }

    @Override
    protected void onServiceStarted() {
        broadcastMessage(Constants.MESSAGE.PPG_SERVICE_STARTED);
    }

    @Override
    protected void onServiceStopped() {
        if (mPPGSensor != null)
            mPPGSensor.stop();
        if (mPPGSensor != null) {
            ((WindowManager) getSystemService(Context.WINDOW_SERVICE)).removeView(mPPGSensor);
        }
        broadcastMessage(Constants.MESSAGE.PPG_SERVICE_STOPPED);
    }

    @Override
    protected void registerSensors() {
        // TODO: Register a PPG listener with the PPG sensor (mPPGSensor)
        mPPGSensor.registerListener(this);
    }

    @Override
    protected void unregisterSensors() {
        // TODO: Unregister the PPG listener
        mPPGSensor.unregisterListeners(); 
    }

    @Override
    protected int getNotificationID() {
        return Constants.NOTIFICATION_ID.PPG_SERVICE;
    }

    @Override
    protected String getNotificationContentText() {
        return getString(R.string.ppg_service_notification);
    }

    @Override
    protected int getNotificationIconResourceID() {
        return R.drawable.ic_whatshot_white_48dp;
    }

    /**
     * This method is called each time a PPG sensor reading is received.
     * <br><br>
     * You should smooth the data using {@link Filter} and then send the filtered data both
     * to the server and the main UI for real-time visualization. Run your algorithm to
     * detect heart beats, calculate your current bpm and send the bmp measurement to the
     * main UI. Additionally, it may be useful for you to send the peaks you detect to
     * the main UI, using {@link #broadcastPeak(long, double)}. The plot is already set up
     * to draw these peak points upon receiving them.
     * <br><br>
     * Also make sure to send your bmp measurement to the server for visualization. You
     * can do this using {@link HRSensorReading}.
     *
     * @param event The PPG sensor reading, wrapping a timestamp and mean red value.
     *
     * @see PPGEvent
     * @see PPGSensorReading
     * @see HeartRateCameraView#onPreviewFrame(byte[], Camera)
     * @see MobileIOClient
     * @see HRSensorReading
     */
    @SuppressWarnings("deprecation")
    @Override
    public void onSensorChanged(PPGEvent event) {
        // TODO: Smooth the signal using a Butterworth / exponential smoothing filter // done
        // TODO: send the data to the UI fragment for visualization, using broadcastPPGReading(...) // done
        // TODO: Send the filtered mean red value to the server // done
        // TODO: Buffer data if necessary for your algorithm //done
        // TODO: Call your heart beat and bpm detection algorithm // done
        // TODO: Send your heart rate estimate to the server // done

        double[] window = new double[3];
        double[] lookahead = new double[3];
        float f = (float) event.value;
        double filteredReading = (double) filter.getFilteredValues(lowpass.getFilteredValues(f))[0];

        PPGSensorReading reading = new PPGSensorReading(mUserID, "Nexus 6p", "hassan", event.timestamp, filteredReading);
        broadcastPPGReading(event.timestamp, filteredReading);
        mClient.sendSensorReading(reading);

        if(timeBuffer.isEmpty()){
            timeBuffer.add(event.timestamp);
            buffer.add(filteredReading);
        }
    //if this event is within the bufferTime window
        if(event.timestamp <timeBuffer.peek()+ bufferTime) {
            timeBuffer.add(event.timestamp);
            buffer.add(filteredReading);
        } else { //otherwise calculate all the peaks and such and then clear and add
            System.out.println("size of the buffer"+buffer.size());
            Log.i(TAG,"size of buffer and size of timeBuffer "+buffer.size()+" "+timeBuffer.size());
            for (int i = 0, j = 1, h = 2; h+3 < timeBuffer.size(); i++, j++, h++) {
                window[0] = buffer.get(i);
                window[1] = buffer.get(j);
                window[2] = buffer.get(h);
                lookahead[0] = buffer.get(i + 3);
                lookahead[1] = buffer.get(j + 3);
                lookahead[2] = buffer.get(h + 3);

                if (window[1] < window[0] && window[1] < window[2]) {
                    //that means our next values after minimum are all increasing so this is a dip
                    if (lookahead[0] < lookahead[1] && lookahead[1] < lookahead[2]) {
                        Log.i(TAG,"adding to the dip buffer");
                        dipBuffer.add(new SignalRep(window[1], timeBuffer.get(j)));
                        broadcastPeak(timeBuffer.get(j),window[1]);
                    }
                }
            }
            double [] sWindow = new double[2];
            LinkedList<Double> differences = new LinkedList<>();
            long meanDiff = 0;
            Log.i(TAG,"size of dipper buffer"+dipBuffer.size());

            for(int i=0; i+1<dipBuffer.size()-1;i++){
                sWindow[0] = dipBuffer.get(i).timestamp;
                sWindow[1] = dipBuffer.get(i+1).timestamp;
                differences.add((sWindow[1]-sWindow[0]));
            }
            Log.i(TAG,"size of difference buffer"+differences.size());

            for (double diff: differences){
                meanDiff+=diff;
            } //estimate the BPM by taking the avg difference between dips. I.E what time till a heart beat occurs. Then divide a bufferTime by that to get an estimate.
            if(differences.size() !=0) {
                meanDiff = meanDiff / differences.size();
                //your heart beats twice. Da-dum
                int bpm = (int) (60000 / meanDiff)*2;
                broadcastBPM(bpm);
                HRSensorReading hrSensorReading = new HRSensorReading(mUserID, "tomas", "tomato123", System.currentTimeMillis(), bpm);
                mClient.sendSensorReading(hrSensorReading);
                timeBuffer.clear();
                buffer.clear();
                buffer.add(filteredReading);
                timeBuffer.add(event.timestamp);
            }
        }

    }


    /**
     * Broadcasts the PPG reading to other application components, e.g. the main UI.
     * @param ppgReading the mean red value.
     */
    public void broadcastPPGReading(final long timestamp, final double ppgReading) {
        Intent intent = new Intent();
        intent.putExtra(Constants.KEY.PPG_DATA, ppgReading);
        intent.putExtra(Constants.KEY.TIMESTAMP, timestamp);
        intent.setAction(Constants.ACTION.BROADCAST_PPG);
        LocalBroadcastManager manager = LocalBroadcastManager.getInstance(this);
        manager.sendBroadcast(intent);
    }

    /**
     * Broadcasts the current heart rate in BPM to other application components, e.g. the main UI.
     * @param bpm the current beats per bufferTime measurement.
     */
    public void broadcastBPM(final int bpm) {
        Intent intent = new Intent();
        intent.putExtra(Constants.KEY.HEART_RATE, bpm);
        intent.setAction(Constants.ACTION.BROADCAST_HEART_RATE);
        LocalBroadcastManager manager = LocalBroadcastManager.getInstance(this);
        manager.sendBroadcast(intent);
    }

    /**
     * Broadcasts the current heart rate in BPM to other application components, e.g. the main UI.
     * @param timestamp the current beats per bufferTime measurement.
     */
    public void broadcastPeak(final long timestamp, final double value) {
        Intent intent = new Intent();
        intent.putExtra(Constants.KEY.PPG_PEAK_TIMESTAMP, timestamp);
        intent.putExtra(Constants.KEY.PPG_PEAK_VALUE, value);
        intent.setAction(Constants.ACTION.BROADCAST_PPG_PEAK);
        LocalBroadcastManager manager = LocalBroadcastManager.getInstance(this);
        manager.sendBroadcast(intent);
    }
}