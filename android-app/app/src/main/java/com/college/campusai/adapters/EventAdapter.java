package com.college.campusai.adapters;

import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.EventModels.EventItem;

import java.util.ArrayList;
import java.util.List;

public class EventAdapter extends RecyclerView.Adapter<EventAdapter.EventViewHolder> {

    public interface OnEventClickListener {
        void onEventClick(EventItem event);
    }

    public interface OnEventLongClickListener {
        void onEventLongClick(EventItem event, View anchor);
    }

    private final List<EventItem> allEvents = new ArrayList<>();
    private final List<EventItem> displayedEvents = new ArrayList<>();
    private OnEventClickListener listener;
    private OnEventLongClickListener longClickListener;
    private String selectedDateFilter = null; // Format "yyyy-MM-dd", or null for all

    public EventAdapter() {}

    public EventAdapter(OnEventClickListener listener) {
        this.listener = listener;
    }

    public void setLongClickListener(OnEventLongClickListener l) {
        this.longClickListener = l;
    }

    public void setEvents(List<EventItem> newEvents) {
        allEvents.clear();
        if (newEvents != null) {
            allEvents.addAll(newEvents);
        }
        applyFilter();
    }

    public void setDateFilter(String dateFilter) {
        this.selectedDateFilter = dateFilter;
        applyFilter();
    }

    private void applyFilter() {
        displayedEvents.clear();
        for (EventItem item : allEvents) {
            if (selectedDateFilter == null || selectedDateFilter.isEmpty()) {
                displayedEvents.add(item);
            } else {
                if (item.startAt != null && item.startAt.startsWith(selectedDateFilter)) {
                    displayedEvents.add(item);
                } else if (item.summary != null && item.summary.contains(selectedDateFilter)) {
                    displayedEvents.add(item);
                }
            }
        }
        notifyDataSetChanged();
    }

    public int getDisplayedCount() {
        return displayedEvents.size();
    }

    @NonNull
    @Override
    public EventViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_event, parent, false);
        return new EventViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull EventViewHolder holder, int position) {
        holder.bind(displayedEvents.get(position), listener, longClickListener);
    }

    @Override
    public int getItemCount() {
        return displayedEvents.size();
    }

    static class EventViewHolder extends RecyclerView.ViewHolder {
        private final TextView tvStartTime;
        private final TextView tvEndTime;
        private final View viewBar;
        private final TextView tvTitle;
        private final TextView tvLocation;
        private final TextView tvTime;
        private final TextView tvType;

        public EventViewHolder(@NonNull View itemView) {
            super(itemView);
            tvStartTime = itemView.findViewById(R.id.tv_event_start_time);
            tvEndTime = itemView.findViewById(R.id.tv_event_end_time);
            viewBar = itemView.findViewById(R.id.view_event_bar);
            tvTitle = itemView.findViewById(R.id.tv_event_title);
            tvLocation = itemView.findViewById(R.id.tv_event_location);
            tvTime = itemView.findViewById(R.id.tv_event_time);
            tvType = itemView.findViewById(R.id.tv_event_type);
        }

        public void bind(EventItem item, OnEventClickListener listener, OnEventLongClickListener longClickListener) {
            tvTitle.setText(item.title != null ? item.title : (item.subject != null ? item.subject : "Class"));
            
            String status = item.status != null ? item.status.toUpperCase() : "CONFIRMED";
            if ("PROPOSED".equals(status)) {
                if (item.summary != null && !item.summary.isEmpty()) {
                    tvLocation.setText("⚠️ " + item.summary);
                } else if (item.location != null) {
                    tvLocation.setText("New Location: " + item.location);
                } else {
                    tvLocation.setText("Faculty Schedule Update (Check details)");
                }
            } else {
                tvLocation.setText(item.location != null ? item.location : "Classroom 602");
            }

            // Extract time
            String startTime = "09:00";
            String endTime = "10:00";

            if (item.startAt != null && item.startAt.contains("T")) {
                String[] parts = item.startAt.split("T");
                if (parts.length > 1 && parts[1].length() >= 5) {
                    startTime = parts[1].substring(0, 5);
                }
            } else if (item.startAt != null && item.startAt.contains(" ")) {
                String[] parts = item.startAt.split(" ");
                if (parts.length > 1 && parts[1].length() >= 5) {
                    startTime = parts[1].substring(0, 5);
                }
            }

            if (item.endAt != null && item.endAt.contains("T")) {
                String[] parts = item.endAt.split("T");
                if (parts.length > 1 && parts[1].length() >= 5) {
                    endTime = parts[1].substring(0, 5);
                }
            } else if (item.endAt != null && item.endAt.contains(" ")) {
                String[] parts = item.endAt.split(" ");
                if (parts.length > 1 && parts[1].length() >= 5) {
                    endTime = parts[1].substring(0, 5);
                }
            } else {
                // Compute 1 hr later default
                try {
                    String[] hm = startTime.split(":");
                    int h = Integer.parseInt(hm[0]) + 1;
                    endTime = String.format("%02d:%s", h, hm[1]);
                } catch (Exception ignored) {
                    endTime = "10:00";
                }
            }

            tvStartTime.setText(startTime);
            tvEndTime.setText(endTime);
            tvTime.setText(item.startAt != null ? item.startAt : "");

            // Status Badge & Bar color
            tvType.setText(status);

            int statusTextColor;
            int statusBgColor;
            int barColor;

            if ("PROPOSED".equals(status)) {
                statusTextColor = Color.parseColor("#7C3AED");
                statusBgColor = Color.parseColor("#F3E8FF");
                barColor = Color.parseColor("#7C3AED");
            } else if ("REJECTED".equals(status)) {
                statusTextColor = Color.parseColor("#DC2626");
                statusBgColor = Color.parseColor("#FEE2E2");
                barColor = Color.parseColor("#DC2626");
            } else {
                statusTextColor = Color.parseColor("#16A34A");
                statusBgColor = Color.parseColor("#DCFCE7");
                barColor = Color.parseColor("#1A237E");
            }

            tvType.setTextColor(statusTextColor);
            GradientDrawable badge = new GradientDrawable();
            badge.setCornerRadius(10f);
            badge.setColor(statusBgColor);
            tvType.setBackground(badge);

            GradientDrawable bar = new GradientDrawable();
            bar.setCornerRadius(6f);
            bar.setColor(barColor);
            viewBar.setBackground(bar);

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onEventClick(item);
                }
            });

            itemView.setOnLongClickListener(v -> {
                if (longClickListener != null) {
                    longClickListener.onEventLongClick(item, v);
                    return true;
                }
                return false;
            });
        }
    }
}
