package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class DashboardResponse {
    @SerializedName("student_name")
    public String studentName;
    @SerializedName("student_email")
    public String studentEmail;
    @SerializedName("unread_email_count")
    public int unreadEmailCount;
    @SerializedName("total_email_count")
    public int totalEmailCount;
    @SerializedName("pending_proposals_count")
    public int pendingProposalsCount;
    @SerializedName("high_priority_emails")
    public List<EmailModels.EmailItem> highPriorityEmails;
    @SerializedName("pending_proposals")
    public List<EventModels.EventItem> pendingProposals;
    @SerializedName("next_class")
    public EventModels.EventItem nextClass;
    @SerializedName("upcoming_schedule")
    public List<EventModels.EventItem> upcomingSchedule;
    @SerializedName("today_schedule")
    public List<EventModels.EventItem> todaySchedule;
}
