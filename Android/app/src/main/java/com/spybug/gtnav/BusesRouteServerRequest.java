package com.spybug.gtnav;

import android.content.Context;
import android.os.AsyncTask;

import com.mapbox.mapboxsdk.geometry.LatLng;
import com.mapbox.services.commons.models.Position;
import com.mapbox.services.commons.utils.PolylineUtils;

import java.lang.ref.WeakReference;
import java.util.List;


/**
 * Background task to get a bus route
 */

public class BusesRouteServerRequest extends AsyncTask<Object, Void, Object> {

    private WeakReference<Context> contextRef;

    BusesRouteServerRequest(Context context) {
        contextRef = new WeakReference<>(context);
    }

    protected void onPreExecute() {
    }

    @Override
    protected Object doInBackground(Object[] objects) {
        LatLng[] points;

        String routeGeometry = "yccmEznbbO??M??J?J?~A?ZAh@AL?B?DCLINEHSXSVGJCDILMTSb@Yr@Mb@CLE\\E^AFGr@QlB" +
                "AF?FADAPKhAq@rHAJAF?DE^Kh@ITIRWb@WZCBSNKFQHA@UFE@SBOB[@]?IAa@AeDK??q@Cg@CI?a@AyAGI??T@zF@x" +
                "A}A?{@CE?a@AG?_@AC?m@??vA?PAjD?dBEDmAAcBAGU?}B?[?Q?I?e@?c@AwA?S?O@O?{F?OAMGOHI|@w@j@g@\\]b@c@d" +
                "@e@PQJIHKESEQCYAW?A?[@[@YDc@Hs@@IHu@BQ@QBM@k@@gE@y@?S?S?O?W?E?u@?K@{@@UBUBMFUBKL[N[DIFIFIFGPMRMJGFC" +
                "JG`Ai@BCBADGDEBEBIBIDO@S?q@@aB?W@W?g@?O?I?Q?M@iB@k@@oC`@AF?p@EZCxAKJ?j@CL?J?J?V@\\?V?F?R?Z@|@?nA@T?R?N?F?" +
                "~BApA@jA@`@?^?P?`@@F?`@B@?ZB\\Hf@Dj@@V@vA?h@??_A?OAMACACECGAE@GBGH?JAL?NBPA^wA?WAk@Ag@E]I?lD?HExA?x@?H?rDAp@?xB[?{@AgBA";

        List<Position> positionList =  PolylineUtils.decode(routeGeometry, 5);

        // Convert Positions List into LatLng[]
        points = new LatLng[positionList.size()];
        for (int i = 0; i < positionList.size(); i++) {
            points[i] = new LatLng(
                    positionList.get(i).getLatitude(),
                    positionList.get(i).getLongitude());
        }

        return points;
    }

    protected void onPostExecute(Object result) {

    }
}
