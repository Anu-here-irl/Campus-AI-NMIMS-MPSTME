package com.college.campusai.api;

import com.college.campusai.models.AuthModels;
import com.college.campusai.models.CampusModels;
import com.college.campusai.models.ChatModels;
import com.college.campusai.models.DashboardResponse;
import com.college.campusai.models.EmailModels;
import com.college.campusai.models.EventModels;

import java.util.List;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {

    // Auth
    @POST("api/v1/auth/login")
    Call<AuthModels.TokenResponse> login(@Body AuthModels.LoginRequest request);

    @POST("api/v1/auth/register")
    Call<AuthModels.UserProfile> register(@Body AuthModels.RegisterRequest request);

    // Dashboard
    @GET("api/v1/dashboard")
    Call<DashboardResponse> getDashboard();

    // Emails & NLP
    @GET("api/v1/emails")
    Call<EmailModels.EmailListResponse> getEmails(
            @Query("category") String category,
            @Query("importance") String importance,
            @Query("unread_only") Boolean unreadOnly,
            @Query("search") String search
    );

    @GET("api/v1/emails/{id}")
    Call<EmailModels.EmailItem> getEmailDetail(@Path("id") int id);

    // Timetable & Proposals
    @GET("api/v1/events")
    Call<List<EventModels.EventItem>> getEvents(@Query("status") String status);

    @GET("api/v1/events/proposals")
    Call<List<EventModels.EventItem>> getPendingProposals();

    @POST("api/v1/events/{id}/confirm")
    Call<EventModels.EventItem> confirmProposal(@Path("id") int id, @Body EventModels.ProposalReviewRequest request);

    @POST("api/v1/events/{id}/reject")
    Call<EventModels.EventItem> rejectProposal(@Path("id") int id, @Body EventModels.ProposalReviewRequest request);

    // Google Calendar Sync & OAuth
    @GET("api/v1/calendar/status")
    Call<EventModels.CalendarStatusResponse> getCalendarStatus();

    @GET("api/v1/calendar/auth-url")
    Call<EventModels.CalendarAuthUrlResponse> getCalendarAuthUrl();

    @POST("api/v1/calendar/sync")
    Call<EventModels.CalendarSyncResponse> syncGoogleCalendar();


    // Campus Map & Routing
    @GET("api/v1/campus/floors")
    Call<List<CampusModels.CampusFloor>> getFloors();

    @GET("api/v1/campus/search")
    Call<List<CampusModels.CampusRoom>> searchRooms(@Query("q") String query);

    @GET("api/v1/campus/routes")
    Call<CampusModels.RouteResponse> getRoute(
            @Query("from_room") String fromRoom,
            @Query("to_room") String toRoom
    );

    // Study Chatbot Q&A
    @POST("api/v1/chat")
    Call<ChatModels.ChatResponse> sendChatMessage(@Body ChatModels.ChatRequest request);

    // Study Notes & Document Library
    @GET("api/v1/notes")
    Call<List<com.college.campusai.models.NoteModels.NoteItem>> getNotes();

    @POST("api/v1/notes/index-samples")
    Call<com.college.campusai.models.NoteModels.IndexSampleResponse> indexSampleNotes();

    @retrofit2.http.DELETE("api/v1/notes/{id}")
    Call<ResponseBody> deleteNote(@Path("id") int id);
}
