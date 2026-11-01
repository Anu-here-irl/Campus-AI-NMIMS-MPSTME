package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class EventModels {

    public static class EventItem implements Serializable {
        public int id;
        @SerializedName("user_id")
        public int userId;
        @SerializedName("source_email_id")
        public Integer sourceEmailId;
        public String title;
        public String subject;
        @SerializedName("event_type")
        public String eventType;
        @SerializedName("start_at")
        public String startAt;
        @SerializedName("end_at")
        public String endAt;
        public String location;
        public String status;
        public String summary;
        @SerializedName("created_at")
        public String createdAt;
        @SerializedName("is_ongoing")
        public Boolean isOngoing;
    }

    public static class ProposalReviewRequest {
        public String action; // "confirm" or "reject"
        @SerializedName("updated_title")
        public String updatedTitle;
        @SerializedName("updated_location")
        public String updatedLocation;

        public ProposalReviewRequest(String action) {
            this.action = action;
        }
    }

    public static class CalendarStatusResponse {
        @SerializedName("is_connected")
        public boolean isConnected;
        public String scope;
        @SerializedName("expires_at")
        public String expiresAt;
    }

    public static class CalendarAuthUrlResponse {
        @SerializedName("auth_url")
        public String authUrl;
        public String state;
        @SerializedName("redirect_uri")
        public String redirectUri;
    }

    public static class CalendarSyncResponse {
        public int total_count;
        @SerializedName("synced_to_events_count")
        public int syncedToEventsCount;
        public String message;
    }
}

