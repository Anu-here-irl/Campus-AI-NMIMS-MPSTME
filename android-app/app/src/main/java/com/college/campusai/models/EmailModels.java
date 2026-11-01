package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

public class EmailModels {

    public static class EmailItem implements Serializable {
        public int id;
        @SerializedName("user_id")
        public int userId;
        @SerializedName("provider_message_id")
        public String providerMessageId;
        public String subject;
        public String sender;
        @SerializedName("sender_role")
        public String senderRole;
        @SerializedName("received_at")
        public String receivedAt;
        @SerializedName("body_text")
        public String bodyText;
        @SerializedName("is_read")
        public boolean isRead;

        // NLP Prediction Fields
        public String category;
        @SerializedName("category_confidence")
        public double categoryConfidence;
        public String importance;
        @SerializedName("importance_confidence")
        public double importanceConfidence;
        public boolean uncertain;
        @SerializedName("review_recommended")
        public boolean reviewRecommended;

        public List<EntityItem> entities;
        @SerializedName("proposed_event")
        public ProposedEventItem proposedEvent;
    }

    public static class EntityItem implements Serializable {
        @SerializedName("entity_type")
        public String entityType;
        public String value;
        @SerializedName("normalized_value")
        public String normalizedValue;
        public double confidence;
    }

    public static class ProposedEventItem implements Serializable {
        public String title;
        public String subject;
        @SerializedName("event_type")
        public String eventType;
        @SerializedName("new_date")
        public String newDate;
        @SerializedName("new_location")
        public String newLocation;
        public String time;
        public String summary;
    }

    public static class EmailListResponse {
        public int total;
        @SerializedName("unread_count")
        public int unreadCount;
        public List<EmailItem> items;
    }
}
