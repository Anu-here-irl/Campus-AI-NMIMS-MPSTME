package com.college.campusai.ui;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.college.campusai.R;
import com.college.campusai.models.NoteModels.NoteItem;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class NoteEditorActivity extends AppCompatActivity {

    public static final String EXTRA_NOTE = "extra_note";
    private static final String PREF_LOCAL_NOTES = "local_notes_storage";
    private static final String KEY_NOTES_LIST = "notes_json";

    private MaterialToolbar toolbar;
    private EditText etTitle;
    private Spinner spinnerSubject;
    private ImageButton btnBold;
    private ImageButton btnItalic;
    private ImageButton btnUnderline;
    private EditText etContent;
    private MaterialButton btnDelete;
    private MaterialButton btnCancel;
    private MaterialButton btnSave;

    private NoteItem existingNote;
    private final String[] subjects = new String[]{"NLP", "CN", "DBMS", "OS", "GENERAL"};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_note_editor);

        toolbar = findViewById(R.id.toolbar_note_editor);
        etTitle = findViewById(R.id.et_note_title);
        spinnerSubject = findViewById(R.id.spinner_note_subject);
        btnBold = findViewById(R.id.btn_format_bold);
        btnItalic = findViewById(R.id.btn_format_italic);
        btnUnderline = findViewById(R.id.btn_format_underline);
        etContent = findViewById(R.id.et_note_content);
        btnDelete = findViewById(R.id.btn_note_delete);
        btnCancel = findViewById(R.id.btn_note_cancel);
        btnSave = findViewById(R.id.btn_note_save);

        toolbar.setNavigationOnClickListener(v -> finish());

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, subjects);
        spinnerSubject.setAdapter(adapter);

        if (getIntent().hasExtra(EXTRA_NOTE)) {
            existingNote = (NoteItem) getIntent().getSerializableExtra(EXTRA_NOTE);
        }

        if (existingNote != null) {
            toolbar.setTitle("Edit Note");
            etTitle.setText(existingNote.title != null ? existingNote.title : "");
            etContent.setText(existingNote.content != null ? existingNote.content : "");

            if (existingNote.subject != null) {
                for (int i = 0; i < subjects.length; i++) {
                    if (subjects[i].equalsIgnoreCase(existingNote.subject)) {
                        spinnerSubject.setSelection(i);
                        break;
                    }
                }
            }
            btnDelete.setVisibility(View.VISIBLE);
        } else {
            toolbar.setTitle("New Study Note");
            btnDelete.setVisibility(View.GONE);
        }

        // Formatting actions
        btnBold.setOnClickListener(v -> applyFormat("**", "**"));
        btnItalic.setOnClickListener(v -> applyFormat("*", "*"));
        btnUnderline.setOnClickListener(v -> applyFormat("<u>", "</u>"));

        btnCancel.setOnClickListener(v -> finish());
        btnSave.setOnClickListener(v -> saveNote());
        btnDelete.setOnClickListener(v -> confirmDelete());
    }

    private void applyFormat(String prefix, String suffix) {
        int start = Math.max(etContent.getSelectionStart(), 0);
        int end = Math.max(etContent.getSelectionEnd(), 0);
        if (start > end) {
            int tmp = start;
            start = end;
            end = tmp;
        }

        String currentText = etContent.getText().toString();
        if (start != end) {
            String selected = currentText.substring(start, end);
            String replacement = prefix + selected + suffix;
            etContent.getText().replace(start, end, replacement);
            etContent.setSelection(start + replacement.length());
        } else {
            etContent.getText().insert(start, prefix + suffix);
            etContent.setSelection(start + prefix.length());
        }
    }

    private void saveNote() {
        String title = etTitle.getText().toString().trim();
        String content = etContent.getText().toString().trim();
        String subject = (String) spinnerSubject.getSelectedItem();

        if (title.isEmpty()) {
            etTitle.setError("Please enter a note title");
            etTitle.requestFocus();
            return;
        }

        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());

        List<NoteItem> notes = loadLocalNotes(this);
        if (existingNote != null) {
            existingNote.title = title;
            existingNote.content = content;
            existingNote.subject = subject;
            existingNote.createdAt = today;

            for (int i = 0; i < notes.size(); i++) {
                if (notes.get(i).id == existingNote.id) {
                    notes.set(i, existingNote);
                    break;
                }
            }
        } else {
            int nextId = (int) (System.currentTimeMillis() % 1000000);
            NoteItem newNote = new NoteItem(nextId, title, subject, content, today);
            notes.add(0, newNote);
        }

        saveLocalNotes(this, notes);
        Toast.makeText(this, "Note saved successfully!", Toast.LENGTH_SHORT).show();
        setResult(RESULT_OK);
        finish();
    }

    private void confirmDelete() {
        new AlertDialog.Builder(this)
                .setTitle("Delete Note")
                .setMessage("Are you sure you want to delete this study note?")
                .setPositiveButton("Delete", (dialog, which) -> {
                    if (existingNote != null) {
                        List<NoteItem> notes = loadLocalNotes(this);
                        notes.removeIf(n -> n.id == existingNote.id);
                        saveLocalNotes(this, notes);
                    }
                    Toast.makeText(this, "Note deleted", Toast.LENGTH_SHORT).show();
                    setResult(RESULT_OK);
                    finish();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    public static List<NoteItem> loadLocalNotes(Context context) {
        SharedPreferences pref = context.getSharedPreferences(PREF_LOCAL_NOTES, Context.MODE_PRIVATE);
        String json = pref.getString(KEY_NOTES_LIST, null);
        if (json == null) {
            return new ArrayList<>();
        }
        Type listType = new TypeToken<ArrayList<NoteItem>>() {}.getType();
        return new Gson().fromJson(json, listType);
    }

    public static void saveLocalNotes(Context context, List<NoteItem> notes) {
        SharedPreferences pref = context.getSharedPreferences(PREF_LOCAL_NOTES, Context.MODE_PRIVATE);
        String json = new Gson().toJson(notes);
        pref.edit().putString(KEY_NOTES_LIST, json).apply();
    }
}
