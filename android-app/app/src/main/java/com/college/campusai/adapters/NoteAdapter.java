package com.college.campusai.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.NoteModels.NoteItem;

import java.util.ArrayList;
import java.util.List;

public class NoteAdapter extends RecyclerView.Adapter<NoteAdapter.NoteViewHolder> {

    public interface OnNoteClickListener {
        void onNoteClick(NoteItem note);
    }

    private final List<NoteItem> allNotes = new ArrayList<>();
    private final List<NoteItem> displayedNotes = new ArrayList<>();
    private final OnNoteClickListener listener;
    private String currentCategory = "All";
    private String currentQuery = "";

    public NoteAdapter(OnNoteClickListener listener) {
        this.listener = listener;
    }

    public void setNotes(List<NoteItem> notes) {
        allNotes.clear();
        if (notes != null) {
            allNotes.addAll(notes);
        }
        applyFilter();
    }

    public void filterByCategory(String category) {
        this.currentCategory = category != null ? category : "All";
        applyFilter();
    }

    public void filterByQuery(String query) {
        this.currentQuery = query != null ? query.trim().toLowerCase() : "";
        applyFilter();
    }

    private void applyFilter() {
        displayedNotes.clear();
        for (NoteItem item : allNotes) {
            boolean matchesCategory = "All".equalsIgnoreCase(currentCategory)
                    || (item.subject != null && item.subject.equalsIgnoreCase(currentCategory));

            boolean matchesQuery = currentQuery.isEmpty()
                    || (item.title != null && item.title.toLowerCase().contains(currentQuery))
                    || (item.content != null && item.content.toLowerCase().contains(currentQuery))
                    || (item.subject != null && item.subject.toLowerCase().contains(currentQuery));

            if (matchesCategory && matchesQuery) {
                displayedNotes.add(item);
            }
        }
        notifyDataSetChanged();
    }

    public int getDisplayedCount() {
        return displayedNotes.size();
    }

    @NonNull
    @Override
    public NoteViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_note, parent, false);
        return new NoteViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull NoteViewHolder holder, int position) {
        NoteItem item = displayedNotes.get(position);
        holder.bind(item, listener);
    }

    @Override
    public int getItemCount() {
        return displayedNotes.size();
    }

    static class NoteViewHolder extends RecyclerView.ViewHolder {
        private final TextView tvSubject;
        private final TextView tvChunks;
        private final TextView tvDate;
        private final TextView tvTitle;
        private final TextView tvPreview;

        public NoteViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSubject = itemView.findViewById(R.id.tv_note_subject);
            tvChunks = itemView.findViewById(R.id.tv_note_chunks);
            tvDate = itemView.findViewById(R.id.tv_note_date);
            tvTitle = itemView.findViewById(R.id.tv_note_title);
            tvPreview = itemView.findViewById(R.id.tv_note_preview);
        }

        public void bind(NoteItem item, OnNoteClickListener listener) {
            tvSubject.setText(item.subject != null && !item.subject.isEmpty() ? item.subject : "GENERAL");

            int chunks = item.totalChunks > 0 ? item.totalChunks : 3;
            tvChunks.setText(String.format("✓ %d Chunks Indexed", chunks));

            String date = item.createdAt != null && item.createdAt.contains(" ")
                    ? item.createdAt.split(" ")[0]
                    : (item.createdAt != null ? item.createdAt : "2026-10-20");
            tvDate.setText(date);

            tvTitle.setText(item.title != null ? item.title : "Untitled Note");

            String preview = item.content != null && !item.content.isEmpty()
                    ? item.content
                    : "Comprehensive Semester 5 notes and reference material for study assistance.";
            tvPreview.setText(preview);

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onNoteClick(item);
                }
            });
        }
    }
}
