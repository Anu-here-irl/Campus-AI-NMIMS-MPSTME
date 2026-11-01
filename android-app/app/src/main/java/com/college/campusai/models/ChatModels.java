package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

public class ChatModels {

    public static class ChatRequest {
        public String message;
        @SerializedName("subject_filter")
        public String subjectFilter;

        public ChatRequest(String message, String subjectFilter) {
            this.message = message;
            this.subjectFilter = subjectFilter;
        }
    }

    public static class ChatResponse {
        public String answer;
        public boolean grounded;
        public List<ChatSource> sources;
        public double confidence;
    }

    public static class ChatSource implements Serializable {
        public String title;
        @SerializedName("chunk_index")
        public int chunkIndex;
        @SerializedName("text_snippet")
        public String textSnippet;
        @SerializedName("page_number")
        public int pageNumber;
    }

    public static class ChatMessage {
        public String text;
        public boolean isUser;
        public List<ChatSource> sources;

        public ChatMessage(String text, boolean isUser, List<ChatSource> sources) {
            this.text = text;
            this.isUser = isUser;
            this.sources = sources;
        }
    }
}
