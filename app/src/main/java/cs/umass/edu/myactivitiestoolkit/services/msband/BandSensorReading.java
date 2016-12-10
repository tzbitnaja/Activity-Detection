package cs.umass.edu.myactivitiestoolkit.services.msband;

import edu.umass.cs.MHLClient.sensors.SensorReading;

/**
 * Created by tzbitnaja on 12/9/2016.
 */

import org.json.JSONException;
import org.json.JSONObject;

import edu.umass.cs.MHLClient.sensors.SensorReading;

public class BandSensorReading extends SensorReading {

    /** The heart rate value. **/
    private final double value;

    /** The acceleration along the x-axis **/
    private final double x;

    /** The acceleration along the y-axis **/
    private final double y;

    /** The acceleration along the z-axis **/
    private final double z;


    /** The change in orientation along the x-axis **/
    private final double gx;

    /** The change in orientation along the y-axis **/
    private final double gy;

    /** The change in orientation along the z-axis **/
    private final double gz;

    public BandSensorReading(String userID, String deviceType, String deviceID, long t, double value, float... values){
        super(userID, deviceType, deviceID, "SENSOR_BAND", t);

        this.value = value;

        this.x = values[0];
        this.y = values[1];
        this.z = values[2];

        this.gx = values[3];
        this.gy = values[4];
        this.gz = values[5];
    }

    public BandSensorReading(String userID, String deviceType, String deviceID, long t, int label, double value, float... values){
        super(userID, deviceType, deviceID, "SENSOR_BAND", t, label);

        this.value = value;

        this.x = values[0];
        this.y = values[1];
        this.z = values[2];

        this.gx = values[3];
        this.gy = values[4];
        this.gz = values[5];
    }

    @Override
    protected JSONObject toJSONObject() {
        JSONObject obj = getBaseJSONObject();
        JSONObject data = new JSONObject();

        try {
            data.put("t", timestamp);

            data.put("x", x);
            data.put("y", y);
            data.put("z", z);

            data.put("gx", gx);
            data.put("gy", gy);
            data.put("gz", gz);

            data.put("value", value);

            obj.put("data", data);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return obj;

    }
}
