package com.college.campusai.ui;

import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.college.campusai.R;
import com.college.campusai.adapters.EventAdapter;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.EventModels;
import com.college.campusai.models.EventModels.CalendarAuthUrlResponse;
import com.college.campusai.models.EventModels.CalendarStatusResponse;
import com.college.campusai.models.EventModels.CalendarSyncResponse;
import com.college.campusai.models.EventModels.EventItem;
import com.google.android.material.button.MaterialButtonToggleGroup;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class TimetableFragment extends Fragment {

    private static final String PREF_CUSTOM_EVENTS = "custom_timetable_events";
    private static final String KEY_EVENTS_LIST = "custom_events_json";

    // Day-specific override storage
    private static final String PREF_DAY_OVERRIDES = "timetable_day_overrides";
    private static final String KEY_DELETED_SET = "deleted_events_set_json";
    private static final String KEY_EDITED_MAP = "edited_events_map_json";

    private TextView tvCalendarStatus;
    private Button btnCalendarAction;
    private ProgressBar progressCalendarSync;
    private TextView tvEventCount;
    private SwipeRefreshLayout swipeRefresh;
    private RecyclerView rvEvents;
    private ProgressBar progressTimetable;
    private TextView tvEmpty;

    // View Switching & Date Controls
    private MaterialButtonToggleGroup toggleView;
    private LinearLayout layoutDateNavigator;
    private ImageButton btnPrevDate;
    private ImageButton btnNextDate;
    private View btnPickDate;
    private TextView tvTimetableDate;
    private TextView tvSectionTitle;
    private FloatingActionButton fabAddEvent;

    private EventAdapter adapter;
    private boolean isCalendarConnected = false;
    private boolean isDailyView = true;
    private final Calendar selectedCalendar = Calendar.getInstance();
    private final List<EventItem> allLoadedEvents = new ArrayList<>();

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_timetable, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        tvCalendarStatus = view.findViewById(R.id.tv_calendar_status);
        btnCalendarAction = view.findViewById(R.id.btn_calendar_action);
        progressCalendarSync = view.findViewById(R.id.progress_calendar_sync);
        tvEventCount = view.findViewById(R.id.tv_event_count);
        swipeRefresh = view.findViewById(R.id.swipe_refresh_timetable);
        rvEvents = view.findViewById(R.id.rv_timetable_events);
        progressTimetable = view.findViewById(R.id.progress_timetable);
        tvEmpty = view.findViewById(R.id.tv_empty_timetable);

        toggleView = view.findViewById(R.id.toggle_timetable_view);
        layoutDateNavigator = view.findViewById(R.id.layout_date_navigator);
        btnPrevDate = view.findViewById(R.id.btn_prev_date);
        btnNextDate = view.findViewById(R.id.btn_next_date);
        btnPickDate = view.findViewById(R.id.btn_pick_date);
        tvTimetableDate = view.findViewById(R.id.tv_timetable_date);
        tvSectionTitle = view.findViewById(R.id.tv_schedule_section_title);
        fabAddEvent = view.findViewById(R.id.fab_add_event);

        adapter = new EventAdapter(event -> showEventDetailsDialog(event));
        adapter.setLongClickListener((event, anchor) -> {
            if (isDailyView) {
                showClassContextMenu(event, anchor);
            }
        });
        rvEvents.setLayoutManager(new LinearLayoutManager(getContext()));
        rvEvents.setAdapter(adapter);

        updateDateDisplay();

        toggleView.addOnButtonCheckedListener((group, checkedId, isChecked) -> {
            if (!isChecked) return;
            if (checkedId == R.id.btn_view_daily) {
                isDailyView = true;
                layoutDateNavigator.setVisibility(View.VISIBLE);
                tvSectionTitle.setText("DAILY SCHEDULE");
                applyCurrentDateFilter();
            } else {
                isDailyView = false;
                layoutDateNavigator.setVisibility(View.GONE);
                tvSectionTitle.setText("WEEKLY TIMETABLE (MON - FRI)");
                adapter.setDateFilter(null);
                updateEventCount();
            }
        });

        btnPrevDate.setOnClickListener(v -> {
            selectedCalendar.add(Calendar.DAY_OF_YEAR, -1);
            updateDateDisplay();
            applyCurrentDateFilter();
        });

        btnNextDate.setOnClickListener(v -> {
            selectedCalendar.add(Calendar.DAY_OF_YEAR, 1);
            updateDateDisplay();
            applyCurrentDateFilter();
        });

        btnPickDate.setOnClickListener(v -> showDatePicker());

        fabAddEvent.setOnClickListener(v -> showAddEventDialog());

        swipeRefresh.setOnRefreshListener(() -> {
            checkCalendarStatus();
            fetchEvents();
        });

        btnCalendarAction.setOnClickListener(v -> {
            if (isCalendarConnected) {
                syncCalendar();
            } else {
                initiateCalendarOAuth();
            }
        });

        checkCalendarStatus();
        fetchEvents();
    }

    private void updateDateDisplay() {
        SimpleDateFormat sdf = new SimpleDateFormat("EEE, dd MMM yyyy", Locale.getDefault());
        tvTimetableDate.setText(sdf.format(selectedCalendar.getTime()));
    }

    private String getCurrentDateString() {
        SimpleDateFormat filterFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
        return filterFormat.format(selectedCalendar.getTime());
    }

    private void applyCurrentDateFilter() {
        if (isDailyView) {
            String dateStr = getCurrentDateString();
            // Build an override-applied list for the selected date
            List<EventItem> overrideApplied = new ArrayList<>();
            for (EventItem ev : allLoadedEvents) {
                if (ev.startAt == null || !ev.startAt.startsWith(dateStr)) continue;
                String key = overrideKey(ev, dateStr);
                if (isDeletedForDate(key)) continue;
                EventItem edited = getEditedForDate(key);
                overrideApplied.add(edited != null ? edited : ev);
            }
            // For the adapter we still pass all events but with overrides injected;
            // rebuild allLoadedEvents with overrides for this date and re-filter
            adapter.setEvents(buildOverrideList(dateStr));
            adapter.setDateFilter(dateStr);
        } else {
            adapter.setEvents(allLoadedEvents);
            adapter.setDateFilter(null);
        }
        updateEventCount();
    }

    /**
     * Returns allLoadedEvents with day-specific edits/deletes applied for the given date.
     * Events for OTHER dates are returned as-is (no override applied).
     */
    private List<EventItem> buildOverrideList(String dateStr) {
        List<EventItem> result = new ArrayList<>();
        for (EventItem ev : allLoadedEvents) {
            if (ev.startAt != null && ev.startAt.startsWith(dateStr)) {
                String key = overrideKey(ev, dateStr);
                if (isDeletedForDate(key)) continue;
                EventItem edited = getEditedForDate(key);
                result.add(edited != null ? edited : ev);
            } else {
                result.add(ev);
            }
        }
        return result;
    }

    private void updateEventCount() {
        int count = adapter.getDisplayedCount();
        tvEventCount.setText(count + " classes");
        tvEmpty.setVisibility(count == 0 ? View.VISIBLE : View.GONE);
    }

    private void showDatePicker() {
        DatePickerDialog dlg = new DatePickerDialog(
                requireContext(),
                (view, year, month, dayOfMonth) -> {
                    selectedCalendar.set(Calendar.YEAR, year);
                    selectedCalendar.set(Calendar.MONTH, month);
                    selectedCalendar.set(Calendar.DAY_OF_MONTH, dayOfMonth);
                    updateDateDisplay();
                    applyCurrentDateFilter();
                },
                selectedCalendar.get(Calendar.YEAR),
                selectedCalendar.get(Calendar.MONTH),
                selectedCalendar.get(Calendar.DAY_OF_MONTH)
        );
        dlg.show();
    }

    // ─────────────────────────────────────────────────────────────────────────
    // LONG-PRESS CONTEXT MENU
    // ─────────────────────────────────────────────────────────────────────────

    private void showClassContextMenu(EventItem event, View anchor) {
        PopupMenu popup = new PopupMenu(requireContext(), anchor);
        popup.getMenu().add(0, 1, 0, "✏️  Edit for today");
        popup.getMenu().add(0, 2, 0, "🗑️  Delete for today");
        popup.getMenu().add(0, 3, 0, "🗺️  View in Map");

        popup.setOnMenuItemClickListener(item -> {
            switch (item.getItemId()) {
                case 1: confirmEdit(event);   return true;
                case 2: confirmDelete(event); return true;
                case 3: navigateToMap(event); return true;
            }
            return false;
        });
        popup.show();
    }

    // ── EDIT ──────────────────────────────────────────────────────────────────

    private void confirmEdit(EventItem event) {
        new AlertDialog.Builder(requireContext())
                .setTitle("Edit class for today only?")
                .setMessage("Changes will only affect today's schedule. The original class remains unchanged on other days.")
                .setPositiveButton("Yes, Edit", (d, w) -> showEditDialog(event))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void showEditDialog(EventItem originalEvent) {
        AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
        builder.setTitle("Edit Class — Today Only");

        LinearLayout layout = new LinearLayout(getContext());
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(48, 24, 48, 12);

        // Title
        final EditText etTitle = new EditText(getContext());
        etTitle.setHint("Subject / Title");
        etTitle.setText(originalEvent.title != null ? originalEvent.title : "");
        layout.addView(etTitle);

        // Location
        final EditText etLocation = new EditText(getContext());
        etLocation.setHint("Room / Location");
        etLocation.setText(originalEvent.location != null ? originalEvent.location : "");
        layout.addView(etLocation);

        // Start time — extract HH:mm from startAt
        final EditText etStart = new EditText(getContext());
        etStart.setHint("Start Time (HH:mm)");
        etStart.setText(extractTime(originalEvent.startAt));
        layout.addView(etStart);

        // End time
        final EditText etEnd = new EditText(getContext());
        etEnd.setHint("End Time (HH:mm)");
        etEnd.setText(extractTime(originalEvent.endAt));
        layout.addView(etEnd);

        builder.setView(layout);
        builder.setPositiveButton("Save", (dialog, which) -> {
            String newTitle    = etTitle.getText().toString().trim();
            String newLocation = etLocation.getText().toString().trim();
            String newStart    = etStart.getText().toString().trim();
            String newEnd      = etEnd.getText().toString().trim();

            if (newTitle.isEmpty()) {
                Toast.makeText(getContext(), "Title cannot be empty", Toast.LENGTH_SHORT).show();
                return;
            }

            // Build edited copy
            EventItem edited = new EventItem();
            edited.id        = originalEvent.id;
            edited.title     = newTitle;
            edited.subject   = originalEvent.subject;
            edited.location  = !newLocation.isEmpty() ? newLocation : originalEvent.location;
            edited.status    = originalEvent.status;
            edited.eventType = originalEvent.eventType;
            edited.summary   = originalEvent.summary;

            // Rebuild ISO timestamps keeping the same date
            String dateStr = getCurrentDateString();
            edited.startAt = dateStr + "T" + (!newStart.isEmpty() ? newStart : extractTime(originalEvent.startAt)) + ":00";
            edited.endAt   = dateStr + "T" + (!newEnd.isEmpty()   ? newEnd   : extractTime(originalEvent.endAt))   + ":00";

            saveEditedEvent(overrideKey(originalEvent, dateStr), edited);
            applyCurrentDateFilter();
            Toast.makeText(getContext(), "Class updated for today ✓", Toast.LENGTH_SHORT).show();
        });
        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    // ── DELETE ────────────────────────────────────────────────────────────────

    private void confirmDelete(EventItem event) {
        new AlertDialog.Builder(requireContext())
                .setTitle("Delete class for today only?")
                .setMessage("\"" + (event.title != null ? event.title : "Class") + "\" will be hidden from today's schedule only.")
                .setPositiveButton("Yes, Delete", (d, w) -> {
                    saveDeletedEvent(overrideKey(event, getCurrentDateString()));
                    applyCurrentDateFilter();
                    Toast.makeText(getContext(), "Class removed for today ✓", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    // ── VIEW IN MAP ───────────────────────────────────────────────────────────

    private void navigateToMap(EventItem event) {
        String location = event.location;
        if (location == null || location.isEmpty()) {
            Toast.makeText(getContext(), "No location info for this class", Toast.LENGTH_SHORT).show();
            return;
        }

        String[] parsed = parseRoomCodeAndFloor(location);
        String floorId  = parsed[0];
        String roomCode = parsed[1];

        if (getActivity() instanceof MainActivity) {
            ((MainActivity) getActivity()).navigateToMap(roomCode, floorId);
        }
    }

    /**
     * Parses a location string like:
     *   "Classroom 602 (Floor 6)"        → ["6",  "CR-602"]
     *   "Computer Lab 601 (Floor 6)"     → ["6",  "CL-601"]
     *   "Drone Theory CR: 504"           → ["5",  "CR-504"]
     *   "NLP CL: 602"                    → ["6",  "CL-602"]
     *   "NLP TR: 401"                    → ["4",  "CR-401"]
     *
     * Returns {"6", "CR-602"} as the default fallback.
     */
    private String[] parseRoomCodeAndFloor(String location) {
        if (location == null) return new String[]{"6", "CR-602"};

        // 1) Try to extract floor from "(Floor N)"
        String floorId = null;
        java.util.regex.Matcher floorMatcher =
                java.util.regex.Pattern.compile("(?i)\\(Floor\\s*(\\w+)\\)").matcher(location);
        if (floorMatcher.find()) {
            floorId = floorMatcher.group(1);
        }

        // 2) Try to extract room number from various patterns:
        //    "Classroom 602", "CR:602", "CR: 602", "CL:601", "TR:401" etc.
        String roomNum = null;
        boolean isLab = location.toLowerCase().contains("lab") || location.toLowerCase().contains("cl:");

        // Pattern: digits 3-char room number
        java.util.regex.Matcher numMatcher =
                java.util.regex.Pattern.compile("(\\d{3})").matcher(location);
        if (numMatcher.find()) {
            roomNum = numMatcher.group(1);
        }

        // Infer floor from first digit of room number if not found
        if (floorId == null && roomNum != null) {
            floorId = String.valueOf(roomNum.charAt(0));
        }
        if (floorId == null) floorId = "6";
        if (roomNum == null) roomNum = "602";

        // Determine prefix: Lab → CL, else → CR
        String prefix = isLab ? "CL" : "CR";

        return new String[]{floorId, prefix + "-" + roomNum};
    }

    // ─────────────────────────────────────────────────────────────────────────
    // DAY-SPECIFIC OVERRIDE STORAGE (SharedPreferences)
    // ─────────────────────────────────────────────────────────────────────────

    /** Unique key: eventId + "_" + date (yyyy-MM-dd) */
    private String overrideKey(EventItem event, String dateStr) {
        return event.id + "_" + dateStr;
    }

    private SharedPreferences getOverridePrefs() {
        return requireContext().getSharedPreferences(PREF_DAY_OVERRIDES, Context.MODE_PRIVATE);
    }

    private void saveDeletedEvent(String key) {
        SharedPreferences prefs = getOverridePrefs();
        String json = prefs.getString(KEY_DELETED_SET, null);
        Type type = new TypeToken<HashSet<String>>() {}.getType();
        Set<String> set = json != null ? new Gson().fromJson(json, type) : new HashSet<>();
        if (set == null) set = new HashSet<>();
        set.add(key);
        prefs.edit().putString(KEY_DELETED_SET, new Gson().toJson(set)).apply();
    }

    private boolean isDeletedForDate(String key) {
        SharedPreferences prefs = getOverridePrefs();
        String json = prefs.getString(KEY_DELETED_SET, null);
        if (json == null) return false;
        Type type = new TypeToken<HashSet<String>>() {}.getType();
        Set<String> set = new Gson().fromJson(json, type);
        return set != null && set.contains(key);
    }

    private void saveEditedEvent(String key, EventItem edited) {
        SharedPreferences prefs = getOverridePrefs();
        String json = prefs.getString(KEY_EDITED_MAP, null);
        Type type = new TypeToken<HashMap<String, EventItem>>() {}.getType();
        Map<String, EventItem> map = json != null ? new Gson().fromJson(json, type) : new HashMap<>();
        if (map == null) map = new HashMap<>();
        map.put(key, edited);
        prefs.edit().putString(KEY_EDITED_MAP, new Gson().toJson(map)).apply();
    }

    @Nullable
    private EventItem getEditedForDate(String key) {
        SharedPreferences prefs = getOverridePrefs();
        String json = prefs.getString(KEY_EDITED_MAP, null);
        if (json == null) return null;
        Type type = new TypeToken<HashMap<String, EventItem>>() {}.getType();
        Map<String, EventItem> map = new Gson().fromJson(json, type);
        return map != null ? map.get(key) : null;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // HELPERS
    // ─────────────────────────────────────────────────────────────────────────

    /** Extract "HH:mm" from an ISO or space-separated datetime string. */
    private String extractTime(String dateTime) {
        if (dateTime == null) return "";
        if (dateTime.contains("T")) {
            String[] p = dateTime.split("T");
            if (p.length > 1 && p[1].length() >= 5) return p[1].substring(0, 5);
        } else if (dateTime.contains(" ")) {
            String[] p = dateTime.split(" ");
            if (p.length > 1 && p[1].length() >= 5) return p[1].substring(0, 5);
        }
        return "";
    }

    // ─────────────────────────────────────────────────────────────────────────
    // EXISTING METHODS (unchanged)
    // ─────────────────────────────────────────────────────────────────────────

    private void showAddEventDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("Add Class or Study Event");

        LinearLayout layout = new LinearLayout(getContext());
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(40, 20, 40, 10);

        final EditText etTitle = new EditText(getContext());
        etTitle.setHint("Subject / Event Title (e.g. NLP Lab)");
        layout.addView(etTitle);

        final EditText etLocation = new EditText(getContext());
        etLocation.setHint("Room / Location (e.g. Lab 3, 2nd Floor)");
        layout.addView(etLocation);

        final EditText etTime = new EditText(getContext());
        etTime.setHint("Start Time (e.g. 11:00)");
        layout.addView(etTime);

        builder.setView(layout);

        builder.setPositiveButton("Add", (dialog, which) -> {
            String title = etTitle.getText().toString().trim();
            String loc = etLocation.getText().toString().trim();
            String time = etTime.getText().toString().trim();

            if (title.isEmpty()) {
                Toast.makeText(getContext(), "Title required", Toast.LENGTH_SHORT).show();
                return;
            }

            String todayStr = getCurrentDateString();
            String fullTime = todayStr + "T" + (!time.isEmpty() ? time : "10:00") + ":00";

            EventItem custom = new EventItem();
            custom.id = (int) (System.currentTimeMillis() % 1000000);
            custom.title = title;
            custom.location = !loc.isEmpty() ? loc : "Room 204";
            custom.startAt = fullTime;
            custom.status = "CONFIRMED";
            custom.eventType = "CUSTOM";

            saveCustomEvent(custom);
            allLoadedEvents.add(custom);
            adapter.setEvents(allLoadedEvents);
            applyCurrentDateFilter();
            Toast.makeText(getContext(), "Added " + title + " to timetable!", Toast.LENGTH_SHORT).show();
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void showEventDetailsDialog(EventItem event) {
        if (getContext() == null || event == null) return;
        new AlertDialog.Builder(getContext())
                .setTitle(event.title != null ? event.title : "Class Details")
                .setMessage(String.format("Location: %s\nTime: %s\nStatus: %s\n%s",
                        event.location != null ? event.location : "Room 204",
                        event.startAt != null ? event.startAt : "Scheduled",
                        event.status != null ? event.status : "CONFIRMED",
                        event.summary != null ? "\nSummary: " + event.summary : ""))
                .setPositiveButton("Close", null)
                .show();
    }

    private void saveCustomEvent(EventItem event) {
        if (getContext() == null) return;
        SharedPreferences pref = getContext().getSharedPreferences(PREF_CUSTOM_EVENTS, Context.MODE_PRIVATE);
        String json = pref.getString(KEY_EVENTS_LIST, null);
        List<EventItem> list = new ArrayList<>();
        if (json != null) {
            Type listType = new TypeToken<ArrayList<EventItem>>() {}.getType();
            list = new Gson().fromJson(json, listType);
        }
        list.add(event);
        pref.edit().putString(KEY_EVENTS_LIST, new Gson().toJson(list)).apply();
    }

    private List<EventItem> loadCustomEvents() {
        if (getContext() == null) return new ArrayList<>();
        SharedPreferences pref = getContext().getSharedPreferences(PREF_CUSTOM_EVENTS, Context.MODE_PRIVATE);
        String json = pref.getString(KEY_EVENTS_LIST, null);
        if (json == null) return new ArrayList<>();
        Type listType = new TypeToken<ArrayList<EventItem>>() {}.getType();
        return new Gson().fromJson(json, listType);
    }

    @Override
    public void onResume() {
        super.onResume();
        checkCalendarStatus();
    }

    private void checkCalendarStatus() {
        ApiClient.getService().getCalendarStatus().enqueue(new Callback<CalendarStatusResponse>() {
            @Override
            public void onResponse(Call<CalendarStatusResponse> call, Response<CalendarStatusResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    isCalendarConnected = response.body().isConnected;
                    if (isCalendarConnected) {
                        tvCalendarStatus.setText("Connected (Google Calendar active)");
                        btnCalendarAction.setText("Sync Now");
                    } else {
                        tvCalendarStatus.setText("Not connected. Link Google Calendar for auto-sync.");
                        btnCalendarAction.setText("Connect");
                    }
                }
            }

            @Override
            public void onFailure(Call<CalendarStatusResponse> call, Throwable t) {
                tvCalendarStatus.setText("Status check failed");
            }
        });
    }

    private void initiateCalendarOAuth() {
        progressCalendarSync.setVisibility(View.VISIBLE);
        btnCalendarAction.setEnabled(false);

        ApiClient.getService().getCalendarAuthUrl().enqueue(new Callback<CalendarAuthUrlResponse>() {
            @Override
            public void onResponse(Call<CalendarAuthUrlResponse> call, Response<CalendarAuthUrlResponse> response) {
                progressCalendarSync.setVisibility(View.GONE);
                btnCalendarAction.setEnabled(true);

                if (response.isSuccessful() && response.body() != null && response.body().authUrl != null) {
                    String url = response.body().authUrl;
                    Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(browserIntent);
                } else {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Could not retrieve OAuth authorization link.", Toast.LENGTH_SHORT).show();
                    }
                }
            }

            @Override
            public void onFailure(Call<CalendarAuthUrlResponse> call, Throwable t) {
                progressCalendarSync.setVisibility(View.GONE);
                btnCalendarAction.setEnabled(true);
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void syncCalendar() {
        progressCalendarSync.setVisibility(View.VISIBLE);
        btnCalendarAction.setEnabled(false);

        ApiClient.getService().syncGoogleCalendar().enqueue(new Callback<CalendarSyncResponse>() {
            @Override
            public void onResponse(Call<CalendarSyncResponse> call, Response<CalendarSyncResponse> response) {
                progressCalendarSync.setVisibility(View.GONE);
                btnCalendarAction.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Synchronized " + response.body().syncedToEventsCount + " events from Google Calendar!", Toast.LENGTH_SHORT).show();
                    }
                    fetchEvents();
                } else {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Sync failed. Reconnecting may be required.", Toast.LENGTH_SHORT).show();
                    }
                }
            }

            @Override
            public void onFailure(Call<CalendarSyncResponse> call, Throwable t) {
                progressCalendarSync.setVisibility(View.GONE);
                btnCalendarAction.setEnabled(true);
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Sync network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void fetchEvents() {
        if (!swipeRefresh.isRefreshing()) {
            progressTimetable.setVisibility(View.VISIBLE);
        }
        tvEmpty.setVisibility(View.GONE);

        ApiClient.getService().getEvents(null).enqueue(new Callback<List<EventItem>>() {
            @Override
            public void onResponse(Call<List<EventItem>> call, Response<List<EventItem>> response) {
                progressTimetable.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                allLoadedEvents.clear();
                if (response.isSuccessful() && response.body() != null) {
                    allLoadedEvents.addAll(response.body());
                }
                allLoadedEvents.addAll(loadCustomEvents());

                adapter.setEvents(allLoadedEvents);
                applyCurrentDateFilter();
            }

            @Override
            public void onFailure(Call<List<EventItem>> call, Throwable t) {
                progressTimetable.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                allLoadedEvents.clear();
                allLoadedEvents.addAll(loadCustomEvents());
                adapter.setEvents(allLoadedEvents);
                applyCurrentDateFilter();
            }
        });
    }
}
