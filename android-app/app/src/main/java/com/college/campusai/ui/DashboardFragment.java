package com.college.campusai.ui;

import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.college.campusai.CampusAiApp;
import com.college.campusai.R;
import com.college.campusai.adapters.EmailAdapter;
import com.college.campusai.adapters.EventAdapter;
import com.college.campusai.adapters.ProposalAdapter;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.DashboardResponse;
import com.college.campusai.models.EmailModels.EmailItem;
import com.college.campusai.models.EventModels;
import com.college.campusai.models.EventModels.EventItem;
import com.google.android.material.card.MaterialCardView;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DashboardFragment extends Fragment {

    private SwipeRefreshLayout swipeRefresh;
    private TextView tvGreeting;
    private TextView tvDate;
    private TextView tvStatUnread;
    private TextView tvStatProposals;
    private TextView tvStatEvents;
    private ProgressBar progressBar;
    private View btnSyncCalendar;

    // Next Class Hero Card
    private MaterialCardView cardNextClass;
    private TextView tvNextClassBadge;
    private TextView tvNextClassTime;
    private TextView tvNextClassTitle;
    private TextView tvNextClassRoom;

    // Quick Actions
    private View btnActionEmails;
    private View btnActionTimetable;
    private View btnActionChat;
    private View btnActionMap;
    private View btnActionNotes;

    // Schedule & Alerts
    private TextView tvScheduleTitle;
    private TextView tvViewAllSchedule;
    private RecyclerView rvSchedule;
    private EventAdapter scheduleAdapter;

    private TextView tvProposalsTitle;
    private RecyclerView rvProposals;
    private ProposalAdapter proposalAdapter;

    private TextView tvUrgentTitle;
    private RecyclerView rvUrgentEmails;
    private EmailAdapter urgentEmailAdapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_dashboard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        swipeRefresh = view.findViewById(R.id.swipe_refresh_dashboard);
        tvGreeting = view.findViewById(R.id.tv_dash_greeting);
        tvDate = view.findViewById(R.id.tv_dash_date);
        tvStatUnread = view.findViewById(R.id.tv_stat_unread);
        tvStatProposals = view.findViewById(R.id.tv_stat_proposals);
        tvStatEvents = view.findViewById(R.id.tv_stat_events);
        progressBar = view.findViewById(R.id.progress_dashboard);
        btnSyncCalendar = view.findViewById(R.id.btn_dash_sync_calendar);

        cardNextClass = view.findViewById(R.id.card_next_class);
        tvNextClassBadge = view.findViewById(R.id.tv_dash_next_class_badge);
        tvNextClassTime = view.findViewById(R.id.tv_dash_next_class_time);
        tvNextClassTitle = view.findViewById(R.id.tv_dash_next_class_title);
        tvNextClassRoom = view.findViewById(R.id.tv_dash_next_class_room);

        btnActionEmails = view.findViewById(R.id.btn_action_emails);
        btnActionTimetable = view.findViewById(R.id.btn_action_timetable);
        btnActionChat = view.findViewById(R.id.btn_action_chat);
        btnActionMap = view.findViewById(R.id.btn_action_map);
        btnActionNotes = view.findViewById(R.id.btn_action_notes);

        tvScheduleTitle = view.findViewById(R.id.tv_dash_schedule_title);
        tvViewAllSchedule = view.findViewById(R.id.tv_dash_view_all_schedule);
        rvSchedule = view.findViewById(R.id.rv_dash_events);

        tvProposalsTitle = view.findViewById(R.id.tv_dash_proposals_title);
        rvProposals = view.findViewById(R.id.rv_dash_proposals);

        tvUrgentTitle = view.findViewById(R.id.tv_dash_urgent_title);
        rvUrgentEmails = view.findViewById(R.id.rv_dash_urgent_emails);

        // Date & Greeting
        updateGreetingAndDate();

        // Proposals setup
        proposalAdapter = new ProposalAdapter(new ProposalAdapter.OnProposalActionListener() {
            @Override
            public void onConfirm(EventItem event) {
                reviewProposal(event.id, "confirm");
            }

            @Override
            public void onReject(EventItem event) {
                reviewProposal(event.id, "reject");
            }
        });
        rvProposals.setLayoutManager(new LinearLayoutManager(getContext()));
        rvProposals.setAdapter(proposalAdapter);

        // Urgent emails setup
        urgentEmailAdapter = new EmailAdapter(email -> {
            Intent intent = new Intent(getContext(), EmailDetailActivity.class);
            intent.putExtra(EmailDetailActivity.EXTRA_EMAIL_ITEM, email);
            startActivity(intent);
        });
        rvUrgentEmails.setLayoutManager(new LinearLayoutManager(getContext()));
        rvUrgentEmails.setAdapter(urgentEmailAdapter);

        // Schedule setup
        scheduleAdapter = new EventAdapter();
        rvSchedule.setLayoutManager(new LinearLayoutManager(getContext()));
        rvSchedule.setAdapter(scheduleAdapter);

        // Quick Actions Listeners
        btnActionEmails.setOnClickListener(v -> navigateToTab(R.id.nav_emails));
        btnActionTimetable.setOnClickListener(v -> navigateToTab(R.id.nav_timetable));
        btnActionChat.setOnClickListener(v -> navigateToTab(R.id.nav_chat));
        btnActionMap.setOnClickListener(v -> navigateToTab(R.id.nav_map));
        btnActionNotes.setOnClickListener(v -> startActivity(new Intent(getContext(), NotesActivity.class)));

        if (tvViewAllSchedule != null) {
            tvViewAllSchedule.setOnClickListener(v -> navigateToTab(R.id.nav_timetable));
        }

        swipeRefresh.setOnRefreshListener(this::loadDashboardData);
        btnSyncCalendar.setOnClickListener(v -> syncCalendar());

        loadDashboardData();
    }

    private void updateGreetingAndDate() {
        String studentName = CampusAiApp.getInstance().getSessionManager().getUserName();
        if (studentName == null || studentName.isEmpty() || "Student".equalsIgnoreCase(studentName)) {
            studentName = "Student";
        }

        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        String greetingPrefix;
        if (hour < 12) {
            greetingPrefix = "Good morning";
        } else if (hour < 17) {
            greetingPrefix = "Good afternoon";
        } else {
            greetingPrefix = "Good evening";
        }

        tvGreeting.setText(String.format("%s, %s! 👋", greetingPrefix, studentName));

        SimpleDateFormat sdf = new SimpleDateFormat("EEEE, dd MMM yyyy", Locale.getDefault());
        tvDate.setText(sdf.format(new Date()));
    }

    private void navigateToTab(int navItemId) {
        if (getActivity() instanceof MainActivity) {
            ((MainActivity) getActivity()).switchToTab(navItemId);
        }
    }

    private void loadDashboardData() {
        if (!swipeRefresh.isRefreshing()) {
            progressBar.setVisibility(View.VISIBLE);
        }

        ApiClient.getService().getDashboard().enqueue(new Callback<DashboardResponse>() {
            @Override
            public void onResponse(Call<DashboardResponse> call, Response<DashboardResponse> response) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    DashboardResponse data = response.body();

                    if (data.studentName != null && !data.studentName.isEmpty()) {
                        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
                        String greetingPrefix = hour < 12 ? "Good morning" : (hour < 17 ? "Good afternoon" : "Good evening");
                        tvGreeting.setText(String.format("%s, %s! 👋", greetingPrefix, data.studentName));
                    }

                    tvStatUnread.setText(String.valueOf(data.unreadEmailCount));
                    tvStatProposals.setText(String.valueOf(data.pendingProposalsCount));
                    int eventCount = data.upcomingSchedule != null ? data.upcomingSchedule.size() : 0;
                    tvStatEvents.setText(String.valueOf(eventCount));

                    // Next Class Hero Card setup (Real-time active / next session)
                    EventItem next = data.nextClass != null ? data.nextClass :
                            (data.upcomingSchedule != null && !data.upcomingSchedule.isEmpty() ? data.upcomingSchedule.get(0) : null);

                    if (next != null) {
                        cardNextClass.setVisibility(View.VISIBLE);

                        String startTime = "09:00";
                        String endTime = "10:00";

                        if (next.startAt != null && next.startAt.contains("T")) {
                            String[] parts = next.startAt.split("T");
                            if (parts.length > 1 && parts[1].length() >= 5) {
                                startTime = parts[1].substring(0, 5);
                            }
                        } else if (next.startAt != null && next.startAt.contains(" ")) {
                            String[] parts = next.startAt.split(" ");
                            if (parts.length > 1 && parts[1].length() >= 5) {
                                startTime = parts[1].substring(0, 5);
                            }
                        }

                        if (next.endAt != null && next.endAt.contains("T")) {
                            String[] parts = next.endAt.split("T");
                            if (parts.length > 1 && parts[1].length() >= 5) {
                                endTime = parts[1].substring(0, 5);
                            }
                        } else if (next.endAt != null && next.endAt.contains(" ")) {
                            String[] parts = next.endAt.split(" ");
                            if (parts.length > 1 && parts[1].length() >= 5) {
                                endTime = parts[1].substring(0, 5);
                            }
                        }

                        boolean isOngoing = Boolean.TRUE.equals(next.isOngoing);
                        if (tvNextClassBadge != null) {
                            if (isOngoing) {
                                tvNextClassBadge.setText("HAPPENING NOW");
                                tvNextClassBadge.setTextColor(Color.parseColor("#B91C1C"));
                                tvNextClassBadge.setBackgroundTintList(ColorStateList.valueOf(Color.parseColor("#FEE2E2")));
                            } else {
                                tvNextClassBadge.setText("NEXT CLASS");
                                tvNextClassBadge.setTextColor(getResources().getColor(R.color.primary));
                                tvNextClassBadge.setBackgroundTintList(ColorStateList.valueOf(getResources().getColor(R.color.primary_light)));
                            }
                        }

                        tvNextClassTime.setText(String.format("%s - %s", startTime, endTime));
                        tvNextClassTitle.setText(next.title != null ? next.title : (next.subject != null ? next.subject : "Lecture"));
                        tvNextClassRoom.setText(next.location != null ? next.location : "Room 204 • Block E");
                    } else {
                        // Keep visible as informative card
                        cardNextClass.setVisibility(View.VISIBLE);
                        if (tvNextClassBadge != null) {
                            tvNextClassBadge.setText("FREE PERIOD");
                            tvNextClassBadge.setTextColor(Color.parseColor("#4B5563"));
                            tvNextClassBadge.setBackgroundTintList(ColorStateList.valueOf(Color.parseColor("#F3F4F6")));
                        }
                        tvNextClassTime.setText("All Classes Finished Today");
                        tvNextClassTitle.setText("No upcoming classes scheduled today");
                        tvNextClassRoom.setText("Check Timetable for upcoming days");
                    }

                    // Proposals
                    if (data.pendingProposals != null && !data.pendingProposals.isEmpty()) {
                        tvProposalsTitle.setVisibility(View.VISIBLE);
                        rvProposals.setVisibility(View.VISIBLE);
                        proposalAdapter.setProposals(data.pendingProposals);
                    } else {
                        tvProposalsTitle.setVisibility(View.GONE);
                        rvProposals.setVisibility(View.GONE);
                    }

                    // Urgent Emails
                    if (data.highPriorityEmails != null && !data.highPriorityEmails.isEmpty()) {
                        tvUrgentTitle.setVisibility(View.VISIBLE);
                        rvUrgentEmails.setVisibility(View.VISIBLE);
                        urgentEmailAdapter.setEmails(data.highPriorityEmails);
                    } else {
                        tvUrgentTitle.setVisibility(View.GONE);
                        rvUrgentEmails.setVisibility(View.GONE);
                    }

                    // Schedule - Show today's full schedule if available, otherwise upcoming sessions
                    List<EventItem> displaySchedule = (data.todaySchedule != null && !data.todaySchedule.isEmpty())
                            ? data.todaySchedule : data.upcomingSchedule;

                    if (displaySchedule != null && !displaySchedule.isEmpty()) {
                        tvScheduleTitle.setVisibility(View.VISIBLE);
                        rvSchedule.setVisibility(View.VISIBLE);
                        scheduleAdapter.setEvents(displaySchedule);
                    } else {
                        tvScheduleTitle.setVisibility(View.GONE);
                        rvSchedule.setVisibility(View.GONE);
                    }
                }
            }

            @Override
            public void onFailure(Call<DashboardResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Could not update dashboard: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void reviewProposal(int eventId, String action) {
        EventModels.ProposalReviewRequest req = new EventModels.ProposalReviewRequest(action);
        Call<EventItem> call = "confirm".equals(action)
                ? ApiClient.getService().confirmProposal(eventId, req)
                : ApiClient.getService().rejectProposal(eventId, req);

        call.enqueue(new Callback<EventItem>() {
            @Override
            public void onResponse(Call<EventItem> call, Response<EventItem> response) {
                if (getContext() != null) {
                    String msg = "confirm".equals(action) ? "Schedule updated!" : "Proposal dismissed.";
                    Toast.makeText(getContext(), msg, Toast.LENGTH_SHORT).show();
                }
                loadDashboardData();
            }

            @Override
            public void onFailure(Call<EventItem> call, Throwable t) {
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Action failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void syncCalendar() {
        btnSyncCalendar.setEnabled(false);
        ApiClient.getService().syncGoogleCalendar().enqueue(new Callback<EventModels.CalendarSyncResponse>() {
            @Override
            public void onResponse(Call<EventModels.CalendarSyncResponse> call, Response<EventModels.CalendarSyncResponse> response) {
                btnSyncCalendar.setEnabled(true);
                if (response.isSuccessful() && response.body() != null) {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Calendar synced! (" + response.body().syncedToEventsCount + " events)", Toast.LENGTH_SHORT).show();
                    }
                    loadDashboardData();
                } else {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Connect Google Calendar under Timetable tab first", Toast.LENGTH_LONG).show();
                    }
                }
            }

            @Override
            public void onFailure(Call<EventModels.CalendarSyncResponse> call, Throwable t) {
                btnSyncCalendar.setEnabled(true);
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Sync error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
}
