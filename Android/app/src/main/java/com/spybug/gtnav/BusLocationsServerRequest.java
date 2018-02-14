package com.spybug.gtnav;

import android.content.Context;
import android.os.AsyncTask;

import android.widget.Toast;

import com.mapbox.mapboxsdk.geometry.LatLng;


import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.ref.WeakReference;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;


import static com.spybug.gtnav.HelperUtil.haveNetworkConnection;

//import retrofit.Response;

/**
 * Background task to communicate with the map server
 */

public class BusLocationsServerRequest extends AsyncTask<Object, Void, Object> {

    private static final String REQUEST_METHOD = "GET";
    private static final int READ_TIMEOUT = 15000;
    private static final int CONNECTION_TIMEOUT = 15000;
    private WeakReference<Context> contextRef;
    private boolean hasNetwork = true;
    private int errorCode = 0;

    BusLocationsServerRequest(Context context) {
        contextRef = new WeakReference<>(context);
    }

    protected void onPreExecute() {
        hasNetwork = haveNetworkConnection(contextRef.get());
    }

    @Override
    protected Object doInBackground(Object[] objects) {
        List<LatLng> pointsList = new ArrayList<>();
        LatLng[] points = new LatLng[0];

        if (!hasNetwork) {
            errorCode = 1;
            return points;
        }


        String inputLine;
        String stringUrl;
        String result;
        String routeGeometry;


        stringUrl = String.format("%sbuses",
                    BuildConfig.API_URL);

        try {
            //Create a URL object holding our url
            URL myUrl = new URL(stringUrl);
            //Create a connection
            HttpURLConnection connection =(HttpURLConnection)
                    myUrl.openConnection();
            //Set methods and timeouts
            connection.setRequestMethod(REQUEST_METHOD);
            connection.setReadTimeout(READ_TIMEOUT);
            connection.setConnectTimeout(CONNECTION_TIMEOUT);

            //Connect to our url
            connection.connect();
            //Create a new InputStreamReader
            InputStreamReader streamReader = new
                    InputStreamReader(connection.getInputStream());
            //Create a new buffered reader and String Builder
            BufferedReader reader = new BufferedReader(streamReader);
            StringBuilder stringBuilder = new StringBuilder();
            //Check if the line we are reading is not null
            while((inputLine = reader.readLine()) != null){
                stringBuilder.append(inputLine);
            }
            //Close our InputStream and Buffered reader
            reader.close();
            streamReader.close();
            //Set our result equal to our stringBuilder
            result = stringBuilder.toString();
        }
        catch(IOException e){
            e.printStackTrace();
            result = null;
        }

        if (result != null) {
            try {
                JSONObject directionsResultJson = new JSONObject(result);
                JSONArray vehicles = directionsResultJson.getJSONObject("body").getJSONArray("vehicle");

                for (int i = 0; i < vehicles.length(); i++) {
                    JSONObject vehicle = vehicles.getJSONObject(i);
                    if(vehicle.getString("@routeTag").equals("red")){
                        pointsList.add(new LatLng(vehicle.getDouble("@lat"),
                                vehicle.getDouble("@lon")));
                    }
                }
            }
            catch(JSONException ex) {
                ex.printStackTrace();
            }

        }

        return pointsList.toArray(points);
    }

    protected void onPostExecute(Object result) {
        if (errorCode != 0) {
            if (errorCode == 1) {
                String info = "You are not connected to the internet. Please try again later.";
                Toast.makeText(contextRef.get(), info, Toast.LENGTH_LONG).show();
            } else if (errorCode == 2) {
                String info = "Could not find location, please try again.";
                Toast.makeText(contextRef.get(), info, Toast.LENGTH_LONG).show();
            }
        }
    }
}
