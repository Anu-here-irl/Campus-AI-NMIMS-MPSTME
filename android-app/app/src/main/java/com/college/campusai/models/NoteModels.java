package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class NoteModels {

    public static class NoteItem implements Serializable {
        @SerializedName("id")
        public int id;

        @SerializedName("title")
        public String title;

        @SerializedName("subject")
        public String subject;

        @SerializedName("file_type")
        public String fileType;

        @SerializedName("status")
        public String status;

        @SerializedName("total_chunks")
        public int totalChunks;

        @SerializedName("created_at")
        public String createdAt;

        // Content field for local notes & note editor
        public String content;

        public NoteItem() {}

        public NoteItem(int id, String title, String subject, String content, String createdAt) {
            this.id = id;
            this.title = title;
            this.subject = subject;
            this.content = content;
            this.createdAt = createdAt;
            this.fileType = "MD";
            this.status = "INDEXED";
        }
    }

    public static class IndexSampleResponse implements Serializable {
        @SerializedName("status")
        public String status;

        @SerializedName("notes_indexed_count")
        public int notesIndexedCount;

        @SerializedName("notes")
        public java.util.List<NoteItem> notes;
    }
}
