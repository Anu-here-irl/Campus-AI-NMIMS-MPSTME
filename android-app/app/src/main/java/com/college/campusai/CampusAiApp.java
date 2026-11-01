package com.college.campusai;

import android.app.Application;
import com.college.campusai.utils.SessionManager;

public class CampusAiApp extends Application {
    private static CampusAiApp instance;
    private SessionManager sessionManager;

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        sessionManager = new SessionManager(this);
    }

    public static CampusAiApp getInstance() {
        return instance;
    }

    public SessionManager getSessionManager() {
        return sessionManager;
    }
}
