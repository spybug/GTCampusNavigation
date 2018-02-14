package com.spybug.gtnav;

import android.content.Context;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;

import com.mapbox.mapboxsdk.annotations.Icon;
import com.mapbox.mapboxsdk.annotations.IconFactory;
import com.mapbox.mapboxsdk.annotations.MarkerOptions;
import com.mapbox.mapboxsdk.annotations.PolylineOptions;
import com.mapbox.mapboxsdk.camera.CameraUpdateFactory;
import com.mapbox.mapboxsdk.geometry.LatLng;
import com.mapbox.mapboxsdk.geometry.LatLngBounds;
import com.mapbox.mapboxsdk.maps.MapView;
import com.mapbox.mapboxsdk.maps.MapboxMap;
import com.mapbox.mapboxsdk.maps.OnMapReadyCallback;

import static com.spybug.gtnav.HelperUtil.drawableToBitmap;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link BusesFragment.OnFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link BusesFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class BusesFragment extends Fragment {
    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    private OnFragmentInteractionListener mListener;

    private MapView mapView;
    private MapboxMap map;

    private Icon bus_icon;

    private static final LatLngBounds GT_BOUNDS = new LatLngBounds.Builder()
            .include(new LatLng(33.753312, -84.421579))
            .include(new LatLng(33.797474, -84.372656))
            .build();

    public BusesFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment DirectionsFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static BusesFragment newInstance(String param1, String param2) {
        BusesFragment fragment = new BusesFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam1 = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        final View v = inflater.inflate(R.layout.fragment_buses, container, false);

        ImageButton directionsButton = v.findViewById(R.id.directions_button);
        directionsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                ((MainActivity) getActivity()).openDirectionsFragment(false);
            }
        });

        ImageButton bikesButton = v.findViewById(R.id.bikes_button);
        bikesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                ((MainActivity) getActivity()).openBikesFragment(false);
            }
        });

        mapView = v.findViewById(R.id.mapView);
        mapView.onCreate(savedInstanceState);

        IconFactory iconFactory = IconFactory.getInstance(v.getContext());

        bus_icon = iconFactory.defaultMarker();

        mapView.getMapAsync(new OnMapReadyCallback() {
            @Override
            public void onMapReady(MapboxMap mapboxMap) {
                map = mapboxMap;
                map.setLatLngBoundsForCameraTarget(GT_BOUNDS);
                try {
                    final LatLng[] points = (LatLng[]) new BusesRouteServerRequest(v.getContext()).execute().get();
                    final LatLng[] buses = (LatLng[]) new BusLocationsServerRequest(v.getContext()).execute().get();
                    drawMarkerlessRoute(points);
                    drawBusLocations(buses);

                }
                catch(Exception e) {
                    e.printStackTrace();
                }
            }
        });

        return v;
    }

    public void drawMarkerlessRoute(LatLng[] points) {
        map.clear();
        //Draw Points on Map
        map.addPolyline(new PolylineOptions()
                .add(points)
                .color(Color.parseColor("red"))
                .width(5));

    }

    public void drawBusLocations(LatLng[] points) {
        for(LatLng point : points) {
            map.addMarker(new MarkerOptions()
                    .position(point)
                    .title("Bus")
                    .icon(bus_icon));
        }
    }

    // TODO: Rename method, update argument and hook method into UI event
    public void onButtonPressed(Uri uri) {
        if (mListener != null) {
            mListener.onFragmentInteraction(uri);
        }
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnFragmentInteractionListener {
        // TODO: Update argument type and name
        void onFragmentInteraction(Uri uri);
    }
}
