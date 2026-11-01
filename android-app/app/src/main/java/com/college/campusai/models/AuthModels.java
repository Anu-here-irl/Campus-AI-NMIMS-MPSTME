package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;

public class AuthModels {

    public static class LoginRequest {
        public String email;
        public String password;

        public LoginRequest(String email, String password) {
            this.email = email;
            this.password = password;
        }
    }

    public static class RegisterRequest {
        public String email;
        public String full_name;
        public String password;
        public String department;
        public int semester;

        public RegisterRequest(String email, String full_name, String password) {
            this.email = email;
            this.full_name = full_name;
            this.password = password;
        }

        public RegisterRequest(String email, String password, String full_name, String department, int semester) {
            this.email = email;
            this.password = password;
            this.full_name = full_name;
            this.department = department;
            this.semester = semester;
        }
    }

    public static class TokenResponse {
        @SerializedName("access_token")
        public String accessToken;

        @SerializedName("token_type")
        public String tokenType;

        @SerializedName("user")
        public UserProfile user;
    }

    public static class UserProfile {
        public int id;
        public String email;
        @SerializedName("full_name")
        public String fullName;
        @SerializedName("created_at")
        public String createdAt;
    }
}
