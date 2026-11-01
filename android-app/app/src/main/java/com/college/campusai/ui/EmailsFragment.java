package com.college.campusai.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.college.campusai.R;
import com.college.campusai.adapters.EmailAdapter;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.EmailModels;
import com.college.campusai.models.EmailModels.EmailItem;
import com.google.android.material.chip.Chip;
import com.google.android.material.chip.ChipGroup;

import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class EmailsFragment extends Fragment {

    private EditText etSearch;
    private ImageView ivClearSearch;
    private ChipGroup chipGroupCategories;
    private Chip chipPriorityHigh;
    private SwipeRefreshLayout swipeRefresh;
    private RecyclerView rvEmails;
    private ProgressBar progressBar;
    private TextView tvEmpty;

    private EmailAdapter adapter;

    private String selectedCategory = null;
    private String selectedImportance = null;
    private String currentSearch = null;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_emails, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        etSearch = view.findViewById(R.id.et_search_emails);
        ivClearSearch = view.findViewById(R.id.iv_clear_search);
        chipGroupCategories = view.findViewById(R.id.chip_group_categories);
        chipPriorityHigh = view.findViewById(R.id.chip_priority_high);
        swipeRefresh = view.findViewById(R.id.swipe_refresh_emails);
        rvEmails = view.findViewById(R.id.rv_emails_list);
        progressBar = view.findViewById(R.id.progress_emails);
        tvEmpty = view.findViewById(R.id.tv_empty_emails);

        adapter = new EmailAdapter(email -> {
            Intent intent = new Intent(getContext(), EmailDetailActivity.class);
            intent.putExtra(EmailDetailActivity.EXTRA_EMAIL_ITEM, email);
            startActivity(intent);
        });
        rvEmails.setLayoutManager(new LinearLayoutManager(getContext()));
        rvEmails.setAdapter(adapter);

        // Chip filtering
        chipGroupCategories.setOnCheckedStateChangeListener((group, checkedIds) -> {
            if (checkedIds.isEmpty()) return;
            int checkedId = checkedIds.get(0);
            if (checkedId == R.id.chip_cat_timetable) {
                selectedCategory = "TIMETABLE";
            } else if (checkedId == R.id.chip_cat_exam) {
                selectedCategory = "EXAM";
            } else if (checkedId == R.id.chip_cat_notice) {
                selectedCategory = "NOTICE";
            } else if (checkedId == R.id.chip_cat_event) {
                selectedCategory = "EVENT";
            } else if (checkedId == R.id.chip_cat_general) {
                selectedCategory = "GENERAL";
            } else {
                selectedCategory = null;
            }
            fetchEmails();
        });

        chipPriorityHigh.setOnCheckedChangeListener((buttonView, isChecked) -> {
            selectedImportance = isChecked ? "HIGH" : null;
            fetchEmails();
        });

        // Search text watcher
        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                String q = s != null ? s.toString().trim() : "";
                ivClearSearch.setVisibility(q.isEmpty() ? View.GONE : View.VISIBLE);
                currentSearch = q.isEmpty() ? null : q;
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        etSearch.setOnEditorActionListener((v, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                fetchEmails();
                return true;
            }
            return false;
        });

        ivClearSearch.setOnClickListener(v -> {
            etSearch.setText("");
            currentSearch = null;
            fetchEmails();
        });

        swipeRefresh.setOnRefreshListener(this::fetchEmails);

        fetchEmails();
    }

    private void fetchEmails() {
        if (!swipeRefresh.isRefreshing()) {
            progressBar.setVisibility(View.VISIBLE);
        }
        tvEmpty.setVisibility(View.GONE);

        ApiClient.getService().getEmails(
                selectedCategory,
                selectedImportance,
                null,
                currentSearch
        ).enqueue(new Callback<EmailModels.EmailListResponse>() {
            @Override
            public void onResponse(Call<EmailModels.EmailListResponse> call, Response<EmailModels.EmailListResponse> response) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    List<EmailItem> items = response.body().items;
                    adapter.setEmails(items);
                    if (items == null || items.isEmpty()) {
                        tvEmpty.setVisibility(View.VISIBLE);
                        tvEmpty.setText("No notices matching the selected filters");
                    } else {
                        tvEmpty.setVisibility(View.GONE);
                    }
                } else {
                    tvEmpty.setVisibility(View.VISIBLE);
                    tvEmpty.setText("Failed to retrieve notices.");
                }
            }

            @Override
            public void onFailure(Call<EmailModels.EmailListResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
                tvEmpty.setVisibility(View.VISIBLE);
                tvEmpty.setText("Network error: " + t.getMessage());
                if (getContext() != null) {
                    Toast.makeText(getContext(), "Error: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
}
