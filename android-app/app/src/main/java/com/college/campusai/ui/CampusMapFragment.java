package com.college.campusai.ui;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.cardview.widget.CardView;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.adapters.RoomSearchAdapter;
import com.college.campusai.adapters.RoomSearchAdapter.SearchResultEntry;
import com.college.campusai.models.CampusMapModels.CampusManifest;
import com.college.campusai.models.CampusMapModels.FloorPlan;
import com.college.campusai.models.CampusMapModels.RoomBlock;
import com.college.campusai.ui.views.BlockMapView;
import com.google.android.material.floatingactionbutton.ExtendedFloatingActionButton;
import com.google.gson.Gson;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class CampusMapFragment extends Fragment {

    private static final String ARG_ROOM_CODE = "room_code";
    private static final String ARG_FLOOR_ID  = "floor_id";

    /** Factory method used when navigating from Timetable → Map with a target room. */
    public static CampusMapFragment newInstance(String roomCode, String floorId) {
        CampusMapFragment f = new CampusMapFragment();
        Bundle args = new Bundle();
        args.putString(ARG_ROOM_CODE, roomCode);
        args.putString(ARG_FLOOR_ID, floorId);
        f.setArguments(args);
        return f;
    }

    // Views
    private Spinner spinnerFloors;
    private EditText etRoomSearch;
    private ImageView btnClearSearch;
    private BlockMapView blockMapView;
    private ExtendedFloatingActionButton fabFitScreen;
    private TextView tvNoMapResults;

    // Search Results Dropdown Overlay
    private CardView cardSearchResults;
    private RecyclerView rvSearchResults;
    private RoomSearchAdapter searchAdapter;

    // Selected Room Details Card
    private CardView cardSelectedRoom;
    private TextView tvDetailCode;
    private TextView tvDetailCategory;
    private TextView tvDetailVerified;
    private TextView tvDetailName;
    private TextView tvDetailFloor;
    private TextView tvDetailNotes;
    private ImageView btnCloseDetail;

    // Data
    private final List<FloorPlan> floors = new ArrayList<>();
    private FloorPlan currentFloor;
    private final List<SearchResultEntry> allSearchEntries = new ArrayList<>();

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_campus_map, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // Bind Views
        spinnerFloors = view.findViewById(R.id.spinner_floors);
        etRoomSearch = view.findViewById(R.id.et_room_search);
        btnClearSearch = view.findViewById(R.id.btn_clear_search);
        blockMapView = view.findViewById(R.id.block_map_view);
        fabFitScreen = view.findViewById(R.id.fab_fit_screen);
        tvNoMapResults = view.findViewById(R.id.tv_no_map_results);

        cardSearchResults = view.findViewById(R.id.card_search_results);
        rvSearchResults = view.findViewById(R.id.rv_search_results);

        cardSelectedRoom = view.findViewById(R.id.card_selected_room);
        tvDetailCode = view.findViewById(R.id.tv_detail_code);
        tvDetailCategory = view.findViewById(R.id.tv_detail_category);
        tvDetailVerified = view.findViewById(R.id.tv_detail_verified);
        tvDetailName = view.findViewById(R.id.tv_detail_name);
        tvDetailFloor = view.findViewById(R.id.tv_detail_floor);
        tvDetailNotes = view.findViewById(R.id.tv_detail_notes);
        btnCloseDetail = view.findViewById(R.id.btn_close_detail);

        // Setup Search Adapter
        searchAdapter = new RoomSearchAdapter((floor, room) -> {
            hideKeyboard();
            cardSearchResults.setVisibility(View.GONE);
            etRoomSearch.setText(room.code);

            // Switch floor if search result belongs to another floor
            if (currentFloor == null || !currentFloor.floorId.equalsIgnoreCase(floor.floorId)) {
                for (int i = 0; i < floors.size(); i++) {
                    if (floors.get(i).floorId.equalsIgnoreCase(floor.floorId)) {
                        spinnerFloors.setSelection(i);
                        break;
                    }
                }
            }

            blockMapView.highlightRoom(room);
            displayRoomDetails(room);
        });

        rvSearchResults.setLayoutManager(new LinearLayoutManager(getContext()));
        rvSearchResults.setAdapter(searchAdapter);

        // Setup Map View Tap Listener
        blockMapView.setOnRoomSelectedListener(new BlockMapView.OnRoomSelectedListener() {
            @Override
            public void onRoomSelected(RoomBlock room) {
                displayRoomDetails(room);
            }

            @Override
            public void onSelectionCleared() {
                cardSelectedRoom.setVisibility(View.GONE);
            }
        });

        // Setup Reset / Fit to Screen Button
        fabFitScreen.setOnClickListener(v -> blockMapView.fitToScreen());

        // Setup Close Detail Card
        btnCloseDetail.setOnClickListener(v -> {
            cardSelectedRoom.setVisibility(View.GONE);
            blockMapView.clearHighlight();
        });

        // Setup Clear Search Button
        btnClearSearch.setOnClickListener(v -> {
            etRoomSearch.setText("");
            cardSearchResults.setVisibility(View.GONE);
            tvNoMapResults.setVisibility(View.GONE);
            blockMapView.clearHighlight();
        });

        // Setup Search TextWatcher
        etRoomSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                performRoomSearch(s != null ? s.toString() : "");
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        // Load Floor Data
        loadCampusFloorsData();

        // Auto-navigate to a room if launched from Timetable → View in Map
        Bundle args = getArguments();
        if (args != null) {
            String targetRoom  = args.getString(ARG_ROOM_CODE);
            String targetFloor = args.getString(ARG_FLOOR_ID);
            if (targetRoom != null && targetFloor != null) {
                // Post so the spinner/adapter has been set up first
                view.post(() -> autoNavigateToRoom(targetFloor, targetRoom));
            }
        }
    }

    private void loadCampusFloorsData() {
        try {
            InputStream is = requireContext().getAssets().open("campus_floors.json");
            InputStreamReader reader = new InputStreamReader(is, StandardCharsets.UTF_8);
            CampusManifest manifest = new Gson().fromJson(reader, CampusManifest.class);
            reader.close();

            floors.clear();
            allSearchEntries.clear();

            if (manifest != null && manifest.floors != null) {
                floors.addAll(manifest.floors);

                for (FloorPlan f : floors) {
                    if (f.rooms != null) {
                        for (RoomBlock r : f.rooms) {
                            allSearchEntries.add(new SearchResultEntry(f, r));
                        }
                    }
                }
            }

            setupFloorSpinner();

        } catch (Exception e) {
            Toast.makeText(getContext(), "Failed to load campus floor plans: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void setupFloorSpinner() {
        if (floors.isEmpty() || getContext() == null) return;

        List<String> floorLabels = new ArrayList<>();
        int groundIndex = 0;
        for (int i = 0; i < floors.size(); i++) {
            FloorPlan f = floors.get(i);
            String label = f.floorName + " (" + f.floorId + ")";
            if (f.rooms != null && !f.rooms.isEmpty()) {
                label += " - " + f.rooms.size() + " rooms";
            }
            floorLabels.add(label);

            if ("G".equalsIgnoreCase(f.floorId) || "Ground Floor".equalsIgnoreCase(f.floorName)) {
                groundIndex = i;
            }
        }

        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                requireContext(),
                android.R.layout.simple_spinner_item,
                floorLabels
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerFloors.setAdapter(adapter);

        spinnerFloors.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                currentFloor = floors.get(position);
                blockMapView.setFloorPlan(currentFloor);
                cardSelectedRoom.setVisibility(View.GONE);
                cardSearchResults.setVisibility(View.GONE);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });

        // Default to Ground Floor (G)
        spinnerFloors.setSelection(groundIndex);
    }

    private void performRoomSearch(String query) {
        if (TextUtils.isEmpty(query.trim())) {
            btnClearSearch.setVisibility(View.GONE);
            cardSearchResults.setVisibility(View.GONE);
            tvNoMapResults.setVisibility(View.GONE);
            return;
        }

        btnClearSearch.setVisibility(View.VISIBLE);
        List<SearchResultEntry> matched = new ArrayList<>();

        for (SearchResultEntry entry : allSearchEntries) {
            if (entry.room.matchesQuery(query)) {
                matched.add(entry);
            }
        }

        searchAdapter.setResults(matched);
        if (matched.isEmpty()) {
            cardSearchResults.setVisibility(View.GONE);
            tvNoMapResults.setVisibility(View.VISIBLE);
            tvNoMapResults.setText("No rooms found for \"" + query.trim() + "\"");
        } else {
            cardSearchResults.setVisibility(View.VISIBLE);
            tvNoMapResults.setVisibility(View.GONE);
        }
    }

    private void displayRoomDetails(RoomBlock room) {
        if (room == null) {
            cardSelectedRoom.setVisibility(View.GONE);
            return;
        }

        tvDetailCode.setText(room.code);
        tvDetailCode.setTextColor(room.getBorderColor());

        tvDetailCategory.setText(room.getCategoryDisplayName());
        tvDetailCategory.setTextColor(room.getBorderColor());

        if (room.verified) {
            tvDetailVerified.setText("✓ Verified Plan");
            tvDetailVerified.setTextColor(Color.parseColor("#059669"));
        } else {
            tvDetailVerified.setText("⚠️ Needs Verification");
            tvDetailVerified.setTextColor(Color.parseColor("#D97706"));
        }

        tvDetailName.setText(room.name);
        String floorInfo = (currentFloor != null ? currentFloor.floorName : "Campus") + " • MPSTME Building";
        tvDetailFloor.setText(floorInfo);

        StringBuilder notesSb = new StringBuilder();
        if (!TextUtils.isEmpty(room.notes)) {
            notesSb.append(room.notes);
        } else {
            notesSb.append("Block coordinates: (").append((int) room.x).append(", ").append((int) room.y)
                    .append(") • Size: ").append((int) room.width).append(" × ").append((int) room.height);
        }
        tvDetailNotes.setText(notesSb.toString());

        cardSelectedRoom.setVisibility(View.VISIBLE);
    }

    private void autoNavigateToRoom(String floorId, String roomCode) {
        // 1. Select the correct floor in the spinner
        for (int i = 0; i < floors.size(); i++) {
            if (floors.get(i).floorId != null && floors.get(i).floorId.equalsIgnoreCase(floorId)) {
                spinnerFloors.setSelection(i);
                break;
            }
        }
        // 2. Find the room and highlight it (post again to wait for spinner selection to render)
        spinnerFloors.post(() -> {
            for (FloorPlan floor : floors) {
                if (floor.floorId != null && floor.floorId.equalsIgnoreCase(floorId)) {
                    if (floor.rooms != null) {
                        for (com.college.campusai.models.CampusMapModels.RoomBlock room : floor.rooms) {
                            if (room.code != null && room.code.equalsIgnoreCase(roomCode)) {
                                blockMapView.highlightRoom(room);
                                displayRoomDetails(room);
                                return;
                            }
                        }
                    }
                }
            }
            // Fallback: try matching by room number suffix across all floors
            String numSuffix = roomCode.replaceAll("[^0-9]", "");
            for (FloorPlan floor : floors) {
                if (floor.rooms != null) {
                    for (com.college.campusai.models.CampusMapModels.RoomBlock room : floor.rooms) {
                        if (room.code != null && room.code.replaceAll("[^0-9]", "").equals(numSuffix)) {
                            blockMapView.highlightRoom(room);
                            displayRoomDetails(room);
                            return;
                        }
                    }
                }
            }
            Toast.makeText(getContext(), "Room " + roomCode + " not found on map", Toast.LENGTH_SHORT).show();
        });
    }

    private void hideKeyboard() {
        if (getActivity() != null && getActivity().getCurrentFocus() != null) {
            InputMethodManager imm = (InputMethodManager) getActivity().getSystemService(Context.INPUT_METHOD_SERVICE);
            if (imm != null) {
                imm.hideSoftInputFromWindow(getActivity().getCurrentFocus().getWindowToken(), 0);
            }
        }
    }
}
