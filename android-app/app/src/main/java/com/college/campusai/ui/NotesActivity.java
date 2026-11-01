package com.college.campusai.ui;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.college.campusai.R;
import com.college.campusai.adapters.NoteAdapter;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.NoteModels.NoteItem;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.ChipGroup;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class NotesActivity extends AppCompatActivity {

    private static final int REQ_EDIT_NOTE = 201;

    private MaterialToolbar toolbar;
    private EditText etSearch;
    private ImageView ivClearSearch;
    private ChipGroup chipGroup;
    private SwipeRefreshLayout swipeRefresh;
    private RecyclerView rvNotes;
    private ProgressBar progressBar;
    private LinearLayout layoutEmpty;
    private MaterialButton btnSeedNotes;
    private FloatingActionButton fabAddNote;

    private NoteAdapter adapter;
    private final List<NoteItem> combinedNotes = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notes);

        toolbar = findViewById(R.id.toolbar_notes);
        etSearch = findViewById(R.id.et_search_notes);
        ivClearSearch = findViewById(R.id.iv_clear_notes_search);
        chipGroup = findViewById(R.id.chip_group_notes_category);
        swipeRefresh = findViewById(R.id.swipe_refresh_notes);
        rvNotes = findViewById(R.id.rv_notes_list);
        progressBar = findViewById(R.id.progress_notes);
        layoutEmpty = findViewById(R.id.layout_empty_notes);
        btnSeedNotes = findViewById(R.id.btn_seed_notes);
        fabAddNote = findViewById(R.id.fab_add_note);

        toolbar.setNavigationOnClickListener(v -> finish());

        adapter = new NoteAdapter(note -> {
            Intent intent = new Intent(this, NoteEditorActivity.class);
            intent.putExtra(NoteEditorActivity.EXTRA_NOTE, note);
            startActivityForResult(intent, REQ_EDIT_NOTE);
        });

        rvNotes.setLayoutManager(new LinearLayoutManager(this));
        rvNotes.setAdapter(adapter);

        swipeRefresh.setOnRefreshListener(this::fetchNotes);

        fabAddNote.setOnClickListener(v -> {
            Intent intent = new Intent(this, NoteEditorActivity.class);
            startActivityForResult(intent, REQ_EDIT_NOTE);
        });

        btnSeedNotes.setOnClickListener(v -> seedSampleNotes());

        setupSearchAndFilters();
        fetchNotes();
    }

    private void setupSearchAndFilters() {
        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                adapter.filterByQuery(s.toString());
                ivClearSearch.setVisibility(s.length() > 0 ? View.VISIBLE : View.GONE);
                updateEmptyState();
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        ivClearSearch.setOnClickListener(v -> etSearch.setText(""));

        chipGroup.setOnCheckedStateChangeListener((group, checkedIds) -> {
            if (checkedIds.isEmpty()) return;
            int id = checkedIds.get(0);
            if (id == R.id.chip_notes_all) {
                adapter.filterByCategory("All");
            } else if (id == R.id.chip_notes_nlp) {
                adapter.filterByCategory("NLP");
            } else if (id == R.id.chip_notes_cn) {
                adapter.filterByCategory("CN");
            } else if (id == R.id.chip_notes_dbms) {
                adapter.filterByCategory("DBMS");
            } else if (id == R.id.chip_notes_os) {
                adapter.filterByCategory("OS");
            } else if (id == R.id.chip_notes_general) {
                adapter.filterByCategory("General");
            }
            updateEmptyState();
        });
    }

    private void fetchNotes() {
        if (!swipeRefresh.isRefreshing()) {
            progressBar.setVisibility(View.VISIBLE);
        }

        ApiClient.getService().getNotes().enqueue(new Callback<List<NoteItem>>() {
            @Override
            public void onResponse(Call<List<NoteItem>> call, Response<List<NoteItem>> response) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                List<NoteItem> backendNotes = response.isSuccessful() && response.body() != null
                        ? response.body()
                        : new ArrayList<>();

                mergeAndDisplayNotes(backendNotes);
            }

            @Override
            public void onFailure(Call<List<NoteItem>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
                mergeAndDisplayNotes(new ArrayList<>());
            }
        });
    }

    private void mergeAndDisplayNotes(List<NoteItem> backendNotes) {
        List<NoteItem> localNotes = NoteEditorActivity.loadLocalNotes(this);

        // Merge: avoid duplicates by id
        Map<Integer, NoteItem> map = new HashMap<>();
        for (NoteItem item : backendNotes) {
            map.put(item.id, item);
        }
        for (NoteItem item : localNotes) {
            map.put(item.id, item);
        }

        combinedNotes.clear();
        combinedNotes.addAll(map.values());

        // Default samples if nothing exists at all
        if (combinedNotes.isEmpty()) {
            populateDefaultSampleNotes();
        }

        adapter.setNotes(combinedNotes);
        updateEmptyState();
    }

    private void populateDefaultSampleNotes() {
        combinedNotes.add(new NoteItem(101, "Tokenization and POS Tagging", "NLP",
                "Natural Language Processing fundamentals: Word vs Subword tokenization (BPE, WordPiece) and Part-of-Speech tagging with Hidden Markov Models.", "2026-10-20"));
        combinedNotes.add(new NoteItem(102, "OSI Model and TCP/IP Architecture", "CN",
                "Computer Networks 7-layer OSI model: Physical, Data Link, Network, Transport, Session, Presentation, Application layers. Flow control and TCP handshakes.", "2026-10-18"));
        combinedNotes.add(new NoteItem(103, "Relational Normalization: 1NF to BCNF", "DBMS",
                "Database Management Systems normalization rules: functional dependencies, lossless decomposition, and dependency preservation up to Boyce-Codd Normal Form.", "2026-10-15"));
        combinedNotes.add(new NoteItem(104, "Process Synchronization and Semaphores", "OS",
                "Operating Systems critical section problem, mutual exclusion with mutex locks, counting semaphores, and Dining Philosophers deadlock avoidance.", "2026-10-12"));
        NoteEditorActivity.saveLocalNotes(this, combinedNotes);
    }

    private void seedSampleNotes() {
        progressBar.setVisibility(View.VISIBLE);
        ApiClient.getService().indexSampleNotes().enqueue(new Callback<com.college.campusai.models.NoteModels.IndexSampleResponse>() {
            @Override
            public void onResponse(Call<com.college.campusai.models.NoteModels.IndexSampleResponse> call, Response<com.college.campusai.models.NoteModels.IndexSampleResponse> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null && response.body().notes != null) {
                    Toast.makeText(NotesActivity.this, "Indexed " + response.body().notesIndexedCount + " sample subject notes!", Toast.LENGTH_SHORT).show();
                    mergeAndDisplayNotes(response.body().notes);
                } else {
                    populateDefaultSampleNotes();
                    adapter.setNotes(combinedNotes);
                    updateEmptyState();
                    Toast.makeText(NotesActivity.this, "Loaded Semester 5 reference notes", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<com.college.campusai.models.NoteModels.IndexSampleResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                populateDefaultSampleNotes();
                adapter.setNotes(combinedNotes);
                updateEmptyState();
                Toast.makeText(NotesActivity.this, "Loaded local offline notes", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateEmptyState() {
        if (adapter.getDisplayedCount() == 0) {
            layoutEmpty.setVisibility(View.VISIBLE);
            rvNotes.setVisibility(View.GONE);
        } else {
            layoutEmpty.setVisibility(View.GONE);
            rvNotes.setVisibility(View.VISIBLE);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_EDIT_NOTE && resultCode == RESULT_OK) {
            fetchNotes();
        }
    }
}
