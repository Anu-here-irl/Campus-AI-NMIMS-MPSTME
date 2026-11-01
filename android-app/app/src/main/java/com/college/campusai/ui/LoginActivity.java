package com.college.campusai.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.college.campusai.CampusAiApp;
import com.college.campusai.R;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.AuthModels;
import com.college.campusai.utils.SessionManager;
import com.google.android.material.textfield.TextInputEditText;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private TextInputEditText etEmail;
    private TextInputEditText etPassword;
    private TextInputEditText etServerUrl;
    private Button btnSignIn;
    private Button btnCreateAccount;
    private ProgressBar progressBar;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        sessionManager = CampusAiApp.getInstance().getSessionManager();

        if (sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, MainActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_login);

        etEmail = findViewById(R.id.et_login_email);
        etPassword = findViewById(R.id.et_login_password);
        etServerUrl = findViewById(R.id.et_server_url);
        btnSignIn = findViewById(R.id.btn_sign_in);
        btnCreateAccount = findViewById(R.id.btn_create_account);
        progressBar = findViewById(R.id.progress_login);

        if (etServerUrl != null) {
            etServerUrl.setText(sessionManager.getBaseUrl());
        }

        btnSignIn.setOnClickListener(v -> performLogin());
        btnCreateAccount.setOnClickListener(v -> performRegister());
    }

    private void performLogin() {
        String email = etEmail.getText() != null ? etEmail.getText().toString().trim() : "";
        String password = etPassword.getText() != null ? etPassword.getText().toString().trim() : "";
        String serverUrl = etServerUrl.getText() != null ? etServerUrl.getText().toString().trim() : "";

        if (TextUtils.isEmpty(email) || TextUtils.isEmpty(password)) {
            Toast.makeText(this, "Please enter both email and password", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!TextUtils.isEmpty(serverUrl)) {
            sessionManager.setBaseUrl(serverUrl);
        }

        setLoading(true);

        AuthModels.LoginRequest req = new AuthModels.LoginRequest(email, password);
        ApiClient.getService().login(req).enqueue(new Callback<AuthModels.TokenResponse>() {
            @Override
            public void onResponse(Call<AuthModels.TokenResponse> call, Response<AuthModels.TokenResponse> response) {
                setLoading(false);
                if (response.isSuccessful() && response.body() != null) {
                    AuthModels.TokenResponse tokenRes = response.body();
                    String name = (tokenRes.user != null && tokenRes.user.fullName != null)
                            ? tokenRes.user.fullName : "Student";
                    sessionManager.saveAuthToken(tokenRes.accessToken, email, name);
                    Toast.makeText(LoginActivity.this, "Welcome " + name + "!", Toast.LENGTH_SHORT).show();
                    startActivity(new Intent(LoginActivity.this, MainActivity.class));
                    finish();
                } else {
                    String msg = "Login failed: Incorrect email or password";
                    if (response.code() == 401) {
                        msg = "Invalid email or credentials.";
                    }
                    Toast.makeText(LoginActivity.this, msg, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<AuthModels.TokenResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(LoginActivity.this, "Connection error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void performRegister() {
        String email = etEmail.getText() != null ? etEmail.getText().toString().trim() : "";
        String password = etPassword.getText() != null ? etPassword.getText().toString().trim() : "";
        String serverUrl = etServerUrl.getText() != null ? etServerUrl.getText().toString().trim() : "";

        if (TextUtils.isEmpty(email) || TextUtils.isEmpty(password)) {
            Toast.makeText(this, "Please enter email and password to register", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!TextUtils.isEmpty(serverUrl)) {
            sessionManager.setBaseUrl(serverUrl);
        }

        setLoading(true);

        AuthModels.RegisterRequest req = new AuthModels.RegisterRequest(
                email, password, "Student User", "Computer Science", 5
        );

        ApiClient.getService().register(req).enqueue(new Callback<AuthModels.UserProfile>() {
            @Override
            public void onResponse(Call<AuthModels.UserProfile> call, Response<AuthModels.UserProfile> response) {
                setLoading(false);
                if (response.isSuccessful()) {
                    Toast.makeText(LoginActivity.this, "Account created successfully! Logging in...", Toast.LENGTH_SHORT).show();
                    performLogin();
                } else {
                    Toast.makeText(LoginActivity.this, "Registration failed: User may already exist.", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<AuthModels.UserProfile> call, Throwable t) {
                setLoading(false);
                Toast.makeText(LoginActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void setLoading(boolean isLoading) {
        if (progressBar != null) {
            progressBar.setVisibility(isLoading ? View.VISIBLE : View.GONE);
        }
        btnSignIn.setEnabled(!isLoading);
        btnCreateAccount.setEnabled(!isLoading);
    }
}
