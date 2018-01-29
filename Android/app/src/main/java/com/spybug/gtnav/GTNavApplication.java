package com.spybug.gtnav;

import android.app.Application;

import com.mapbox.mapboxsdk.Mapbox;


public class GTNavApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();

        // Mapbox Access token
        Mapbox.getInstance(getApplicationContext(), getString(R.string.mapbox_key));
    }

}
