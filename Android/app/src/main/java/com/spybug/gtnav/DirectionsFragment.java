package com.spybug.gtnav;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.media.Image;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import com.mapbox.mapboxsdk.annotations.Icon;
import com.mapbox.mapboxsdk.annotations.IconFactory;
import com.mapbox.mapboxsdk.annotations.MarkerOptions;
import com.mapbox.mapboxsdk.annotations.PolylineOptions;
import com.mapbox.mapboxsdk.camera.CameraPosition;
import com.mapbox.mapboxsdk.camera.CameraUpdateFactory;
import com.mapbox.mapboxsdk.constants.Style;
import com.mapbox.mapboxsdk.geometry.LatLng;
import com.mapbox.mapboxsdk.geometry.LatLngBounds;
import com.mapbox.mapboxsdk.maps.MapView;
import com.mapbox.mapboxsdk.maps.MapboxMap;
import com.mapbox.mapboxsdk.maps.MapboxMapOptions;
import com.mapbox.mapboxsdk.maps.OnMapReadyCallback;

import static com.spybug.gtnav.HelperUtil.drawableToBitmap;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link DirectionsFragment.OnFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link DirectionsFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DirectionsFragment extends Fragment {
    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    private MapView mapView;
    private MapboxMap map;

    private static final LatLngBounds GT_BOUNDS = new LatLngBounds.Builder()
            .include(new LatLng(33.753312, -84.421579))
            .include(new LatLng(33.797474, -84.372656))
            .build();

    private Icon start_icon, destination_icon;

    private OnFragmentInteractionListener mListener;

    public DirectionsFragment() {
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
    public static DirectionsFragment newInstance(String param1, String param2) {
        DirectionsFragment fragment = new DirectionsFragment();
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
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_directions, container, false);

        ImageButton backButton = v.findViewById(R.id.directions_back_button);
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                getActivity().onBackPressed();
            }
        });

        ImageButton busesButton = v.findViewById(R.id.buses_button);
        busesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                ((MainActivity) getActivity()).openBusesFragment(false);
            }
        });

        ImageButton bikesButton = v.findViewById(R.id.bikes_button);
        bikesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                ((MainActivity) getActivity()).openBikesFragment(false);
            }
        });

        final EditText startLocation = v.findViewById(R.id.start_location);
        final EditText endLocation = v.findViewById(R.id.end_location);
        final View myView = v;

        mapView = v.findViewById(R.id.mapView);
        mapView.onCreate(savedInstanceState);

        mapView.getMapAsync(new OnMapReadyCallback() {
            @Override
            public void onMapReady(MapboxMap mapboxMap) {
                map = mapboxMap;
                map.setLatLngBoundsForCameraTarget(GT_BOUNDS);
            }
        });


        Resources resources = getResources();
        IconFactory iconFactory = IconFactory.getInstance(v.getContext());
        Drawable startMarkerDrawable = resources.getDrawable(R.drawable.start_marker);

        Bitmap start_marker_icon = drawableToBitmap(startMarkerDrawable);
        start_icon = iconFactory.fromBitmap(start_marker_icon);
        destination_icon = iconFactory.defaultMarker();

        endLocation.setOnEditorActionListener(new EditText.OnEditorActionListener() {
            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_DONE) {
                    if (startLocation.getText().length() == 0 || endLocation.getText().length() == 0) {
                        return true;
                    }

                    //hide the keyboard
                    InputMethodManager imm = (InputMethodManager) v.getContext().getSystemService(Context.INPUT_METHOD_SERVICE);
                    imm.hideSoftInputFromWindow(v.getWindowToken(), 0);

                    try {
                        new MapServerRequest(v.getContext(), new OnEventListener<LatLng[], String>() {
                            @Override
                            public void onSuccess(LatLng[] points) {
                                drawPoints(points);
                            }

                            @Override
                            public void onFailure(String message) {
                                Toast.makeText(myView.getContext(), message, Toast.LENGTH_LONG).show();
                            }
                        }).execute(myView, getString(R.string.mapbox_key));

                        return false;
                    }
                    catch(Exception e) {
                        e.printStackTrace();
                        return false;
                    }
                }
                else {
                    return false;
                }
            }
        });


        return v;
    }

    public void drawPoints(LatLng[] points) {
        map.clear();
        //Draw Points on Map
        map.addPolyline(new PolylineOptions()
                .add(points)
                .color(Color.parseColor("red"))
                .width(5));

        LatLng firstPoint = points[0];
        LatLng lastPoint  = points[points.length - 1];

        LatLngBounds latLngBounds = new LatLngBounds.Builder()
                .include(firstPoint)
                .include(lastPoint)
                .build();

        map.easeCamera(CameraUpdateFactory.newLatLngBounds(latLngBounds, 250), 2500);

        map.addMarker(new MarkerOptions()
                .position(firstPoint)
                .title("Start")
                .icon(start_icon));

        map.addMarker(new MarkerOptions()
                .position(lastPoint)
                .title("Destination")
                .icon(destination_icon));

        //<stop tag="ferstcher" title="Tech Tower" lat="33.7722845" lon="-84.39548" stopId="0012"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7722845,-84.39548))
                .title("Tech Tower")
                .icon(destination_icon));

        //<stop tag="hubfers" title="HUB/Ferst Dr" lat="33.7727399" lon="-84.3970599" stopId="0085"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7727399,-84.3970599))
                .title("HUB/Ferst Dr")
                .icon(destination_icon));

        //<stop tag="centrstud" title="Student Center" lat="33.7734596" lon="-84.3991581" stopId="0044"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7734596,-84.3991581))
                .title("Student Center")
                .icon(destination_icon));

        //<stop tag="creccent" title="Recreation Center" lat="33.775097" lon="-84.4023891" stopId="0038"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.775097,-84.4023891))
                .title("Recreation Center")
                .icon(destination_icon));

        //<stop tag="fitthall" title="Fitten Hall" lat="33.778273" lon="-84.4041911" stopId="0022"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.778273,-84.4041911))
                .title("Fitten Hall")
                .icon(destination_icon));

        //<stop tag="8thwvil" title="8th St & West Village" shortTitle="8th & West Village" lat="33.779616" lon="-84.4047091" stopId="0030"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.779616,-84.4047091))
                .title("8th St & West Village")
                .icon(destination_icon));

        //<stop tag="8thhemp" title="8th St & Hemphill Ave" shortTitle="8th & Hemphill" lat="33.779631" lon="-84.4027473" stopId="0006"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.779631,-84.4027473))
                .title("8th St & Hemphill")
                .icon(destination_icon));

        //<stop tag="fershemp" title="Ferst Dr & Hemphill Ave" shortTitle="Ferst Dr & Hemphill" lat="33.7784499" lon="-84.4008237" stopId="0017"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7784499,-84.4008237))
                .title("Ferst Dr & Hemphill")
                .icon(destination_icon));

        //<stop tag="fersatla" title="Ferst Dr & Atlantic Dr" lat="33.77819" lon="-84.3974904" stopId="0015"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.77819,-84.3974904))
                .title("Ferst Dr & Atlantic Dr")
                .icon(destination_icon));

        //<stop tag="klaubldg" title="Klaus Building" lat="33.7770973" lon="-84.3954843" stopId="0019"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7770973,-84.3954843))
                .title("Klaus Building")
                .icon(destination_icon));

        //<stop tag="fersfowl" title="Ferst Dr & Fowler St" shortTitle="Ferst Dr & Fowler" lat="33.776893" lon="-84.3937807" stopId="0003"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.776893,-84.3937807))
                .title("Ferst Dr & Fowler")
                .icon(destination_icon));

        //<stop tag="tech5th" title="Techwood Dr & 5th St" shortTitle="Techwood Dr & 5th" lat="33.7766855" lon="-84.3921335" stopId="0054"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7766855,-84.3921335))
                .title("Techwood Dr & 5th")
                .icon(destination_icon));

        //<stop tag="tech4th" title="Techwood Dr & 4th St" shortTitle="Techwood Dr & 4th" lat="33.7749537" lon="-84.3920488" stopId="0052"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7749537,-84.3920488))
                .title("Techwood Dr & 4th")
                .icon(destination_icon));

        //<stop tag="techbob" title="Techwood Dr & Bobby Dodd Way" lat="33.7736674" lon="-84.3920495" stopId="0055"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7736674,-84.3920495))
                .title("Techwood Dr & Bobby Dodd Way")
                .icon(destination_icon));

        //<stop tag="technorth" title="Techwood Dr & North Ave" shortTitle="Techwood Dr & North" lat="33.7714502" lon="-84.3920986" stopId="0057"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7714502,-84.3920986))
                .title("Techwood Dr & North Ave")
                .icon(destination_icon));

        //<stop tag="naveapts_a" title="North Avenue Apartments - Arrival" shortTitle="North Apartments - Arrival" lat="33.7699398" lon="-84.3916292" stopId="0067"/>
        map.addMarker(new MarkerOptions()
                .position(new LatLng(33.7699398,-84.3916292))
                .title("North Ave Apartments")
                .icon(destination_icon));
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
