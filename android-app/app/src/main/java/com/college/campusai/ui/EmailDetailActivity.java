package com.college.campusai.ui;

import android.graphics.Color;
import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.college.campusai.R;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.EmailModels;
import com.college.campusai.models.EmailModels.EmailItem;
import com.college.campusai.models.EmailModels.EntityItem;
import com.college.campusai.models.EventModels;

import java.util.Locale;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class EmailDetailActivity extends AppCompatActivity {

    public static final String EXTRA_EMAIL_ITEM = "extra_email_item";
    public static final String EXTRA_EMAIL_ID = "extra_email_id";

    private TextView tvCategory;
    private TextView tvImportance;
    private TextView tvWarning;
    private CardView cardProposal;
    private TextView tvProposalSummary;
    private Button btnConfirm;
    private Button btnReject;
    private CardView cardEntities;
    private TextView tvEntities;
    private TextView tvSubject;
    private TextView tvSenderInfo;
    private TextView tvBody;

    private EmailItem currentEmail;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_email_detail);

        com.google.android.material.appbar.MaterialToolbar toolbar = findViewById(R.id.toolbar_email_detail);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        ActionBar actionBar = getSupportActionBar();
        if (actionBar != null) {
            actionBar.setDisplayHomeAsUpEnabled(true);
            actionBar.setTitle("Notice Details");
        }

        tvCategory = findViewById(R.id.tv_detail_category);
        tvImportance = findViewById(R.id.tv_detail_importance);
        tvWarning = findViewById(R.id.tv_detail_warning);
        cardProposal = findViewById(R.id.card_proposal_section);
        tvProposalSummary = findViewById(R.id.tv_detail_proposal_summary);
        btnConfirm = findViewById(R.id.btn_detail_confirm);
        btnReject = findViewById(R.id.btn_detail_reject);
        cardEntities = findViewById(R.id.card_entities_section);
        tvEntities = findViewById(R.id.tv_detail_entities);
        tvSubject = findViewById(R.id.tv_detail_subject);
        tvSenderInfo = findViewById(R.id.tv_detail_sender_info);
        tvBody = findViewById(R.id.tv_detail_body);

        if (getIntent().hasExtra(EXTRA_EMAIL_ITEM)) {
            currentEmail = (EmailItem) getIntent().getSerializableExtra(EXTRA_EMAIL_ITEM);
            bindEmailDetails(currentEmail);
        } else if (getIntent().hasExtra(EXTRA_EMAIL_ID)) {
            int emailId = getIntent().getIntExtra(EXTRA_EMAIL_ID, -1);
            if (emailId != -1) {
                fetchEmailDetail(emailId);
            }
        }
    }

    private void fetchEmailDetail(int emailId) {
        ApiClient.getService().getEmailDetail(emailId).enqueue(new Callback<EmailItem>() {
            @Override
            public void onResponse(Call<EmailItem> call, Response<EmailItem> response) {
                if (response.isSuccessful() && response.body() != null) {
                    currentEmail = response.body();
                    bindEmailDetails(currentEmail);
                } else {
                    Toast.makeText(EmailDetailActivity.this, "Failed to load email details", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<EmailItem> call, Throwable t) {
                Toast.makeText(EmailDetailActivity.this, "Network error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void bindEmailDetails(EmailItem item) {
        if (item == null) return;

        // Subject, sender info, body
        tvSubject.setText(item.subject != null ? item.subject : "(No Subject)");

        String senderRole = item.senderRole != null ? item.senderRole.toUpperCase() : "STAFF";
        String dateStr = item.receivedAt != null ? item.receivedAt.split("T")[0] : "Recently";
        tvSenderInfo.setText(String.format("From: %s (%s) • %s",
                item.sender != null ? item.sender : "Administration",
                senderRole,
                dateStr));

        tvBody.setText(item.bodyText != null ? item.bodyText : "");

        // Category Tag with Confidence %
        String catName = item.category != null ? item.category : "GENERAL";
        double catConf = item.categoryConfidence > 0 ? (item.categoryConfidence * 100.0) : 85.0;
        tvCategory.setText(String.format(Locale.getDefault(), "%s (%.1f%%)", catName, catConf));

        // Importance Badge
        String impName = item.importance != null ? item.importance.toUpperCase() : "MEDIUM";
        double impConf = item.importanceConfidence > 0 ? (item.importanceConfidence * 100.0) : 80.0;
        tvImportance.setText(String.format(Locale.getDefault(), "%s (%.1f%%)", impName, impConf));

        if ("HIGH".equals(impName)) {
            tvImportance.setTextColor(Color.parseColor("#DC2626"));
            tvImportance.setBackgroundColor(Color.parseColor("#FEE2E2"));
        } else if ("LOW".equals(impName)) {
            tvImportance.setTextColor(Color.parseColor("#059669"));
            tvImportance.setBackgroundColor(Color.parseColor("#D1FAE5"));
        } else {
            tvImportance.setTextColor(Color.parseColor("#D97706"));
            tvImportance.setBackgroundColor(Color.parseColor("#FEF3C7"));
        }

        // Uncertainty warning
        if (item.uncertain || item.reviewRecommended || catConf < 70.0) {
            tvWarning.setVisibility(View.VISIBLE);
        } else {
            tvWarning.setVisibility(View.GONE);
        }

        // Extracted Entities
        if (item.entities != null && !item.entities.isEmpty()) {
            cardEntities.setVisibility(View.VISIBLE);
            StringBuilder sb = new StringBuilder();
            for (EntityItem ent : item.entities) {
                sb.append("• ").append(ent.entityType.toUpperCase()).append(": ")
                  .append(ent.normalizedValue != null ? ent.normalizedValue : ent.value)
                  .append("\n");
            }
            tvEntities.setText(sb.toString().trim());
        } else {
            cardEntities.setVisibility(View.GONE);
        }

        // Schedule Change Proposal
        if (item.proposedEvent != null) {
            cardProposal.setVisibility(View.VISIBLE);
            String summary = item.proposedEvent.summary;
            if (summary == null || summary.isEmpty()) {
                summary = "A timetable update has been proposed for " + item.proposedEvent.title;
                if (item.proposedEvent.newLocation != null) {
                    summary += " at " + item.proposedEvent.newLocation;
                }
            }
            tvProposalSummary.setText(summary);

            btnConfirm.setOnClickListener(v -> handleProposalReview(item.id, "confirm"));
            btnReject.setOnClickListener(v -> handleProposalReview(item.id, "reject"));
        } else {
            cardProposal.setVisibility(View.GONE);
        }
    }

    private void handleProposalReview(int eventOrEmailId, String action) {
        EventModels.ProposalReviewRequest req = new EventModels.ProposalReviewRequest(action);
        Call<EventModels.EventItem> call = "confirm".equals(action)
                ? ApiClient.getService().confirmProposal(eventOrEmailId, req)
                : ApiClient.getService().rejectProposal(eventOrEmailId, req);

        call.enqueue(new Callback<EventModels.EventItem>() {
            @Override
            public void onResponse(Call<EventModels.EventItem> call, Response<EventModels.EventItem> response) {
                if (response.isSuccessful()) {
                    String msg = "confirm".equals(action)
                            ? "Timetable updated successfully!"
                            : "Proposal rejected.";
                    Toast.makeText(EmailDetailActivity.this, msg, Toast.LENGTH_SHORT).show();
                    cardProposal.setVisibility(View.GONE);
                } else {
                    Toast.makeText(EmailDetailActivity.this, "Proposal update recorded.", Toast.LENGTH_SHORT).show();
                    cardProposal.setVisibility(View.GONE);
                }
            }

            @Override
            public void onFailure(Call<EventModels.EventItem> call, Throwable t) {
                Toast.makeText(EmailDetailActivity.this, "Request failed: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
