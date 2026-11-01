package com.college.campusai.utils;

import android.content.Context;
import android.content.SharedPreferences;

public class SessionManager {
    private static final String PREF_NAME = "campus_ai_session";
    private static final String KEY_TOKEN = "jwt_token";
    private static final String KEY_USER_EMAIL = "user_email";
    private static final String KEY_USER_NAME = "user_name";
    private static final String KEY_BASE_URL = "base_url";

    public static final String DEFAULT_BASE_URL = "http://127.0.0.1:8000/";

    private final SharedPreferences pref;
    private final SharedPreferences.Editor editor;

    public SessionManager(Context context) {
        pref = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        editor = pref.edit();
    }

    public void saveAuthToken(String token, String email, String name) {
        editor.putString(KEY_TOKEN, token);
        editor.putString(KEY_USER_EMAIL, email);
        editor.putString(KEY_USER_NAME, name);
        editor.apply();
    }

    public String getAuthToken() {
        return pref.getString(KEY_TOKEN, null);
    }

    public boolean isLoggedIn() {
        return getAuthToken() != null;
    }

    public void setBaseUrl(String url) {
        if (url == null || url.trim().isEmpty()) {
            url = DEFAULT_BASE_URL;
        } else {
            url = url.trim();
            if (!url.startsWith("http://") && !url.startsWith("https://")) {
                url = "http://" + url;
            }
            if (!url.matches("^https?://[^/]+:[0-9]+.*$")) {
                if (url.endsWith("/")) {
                    url = url.substring(0, url.length() - 1) + ":8000/";
                } else {
                    url = url + ":8000/";
                }
            }
            if (!url.endsWith("/")) {
                url += "/";
            }
        }
        editor.putString(KEY_BASE_URL, url);
        editor.apply();
    }

    public String getBaseUrl() {
        return pref.getString(KEY_BASE_URL, DEFAULT_BASE_URL);
    }

    public String getUserName() {
        return pref.getString(KEY_USER_NAME, "Student");
    }

    public String getUserEmail() {
        return pref.getString(KEY_USER_EMAIL, "student@campus.edu");
    }

    public void clear() {
        editor.remove(KEY_TOKEN);
        editor.remove(KEY_USER_EMAIL);
        editor.remove(KEY_USER_NAME);
        editor.apply();
    }
}
