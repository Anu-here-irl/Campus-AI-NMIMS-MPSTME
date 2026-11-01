package com.college.campusai.ui;

import android.os.Bundle;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.adapters.ChatAdapter;
import com.college.campusai.api.ApiClient;
import com.college.campusai.models.ChatModels;
import com.college.campusai.models.ChatModels.ChatMessage;
import com.college.campusai.models.ChatModels.ChatResponse;
import com.google.android.material.button.MaterialButton;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ChatFragment extends Fragment {

    private RecyclerView rvChat;
    private View layoutEmpty;
    private EditText etInput;
    private ImageButton btnSend;
    private ProgressBar progressBar;

    private ChatAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_chat, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        rvChat = view.findViewById(R.id.rv_chat_messages);
        layoutEmpty = view.findViewById(R.id.layout_chat_empty);
        etInput = view.findViewById(R.id.et_chat_input);
        btnSend = view.findViewById(R.id.btn_send_chat);
        progressBar = view.findViewById(R.id.progress_chat_send);

        adapter = new ChatAdapter();
        LinearLayoutManager layoutManager = new LinearLayoutManager(getContext());
        layoutManager.setStackFromEnd(true);
        rvChat.setLayoutManager(layoutManager);
        rvChat.setAdapter(adapter);

        btnSend.setOnClickListener(v -> sendMessage());
    }

    private void sendMessage() {
        String query = etInput.getText() != null ? etInput.getText().toString().trim() : "";
        if (TextUtils.isEmpty(query)) {
            return;
        }

        if (layoutEmpty != null) {
            layoutEmpty.setVisibility(View.GONE);
        }

        // Add user message to conversation list
        adapter.addMessage(new ChatMessage(query, true, null));
        rvChat.smoothScrollToPosition(adapter.getItemCount() - 1);
        etInput.setText("");

        // Show sending state
        progressBar.setVisibility(View.VISIBLE);
        btnSend.setEnabled(false);

        ChatModels.ChatRequest req = new ChatModels.ChatRequest(query, null);
        ApiClient.getService().sendChatMessage(req).enqueue(new Callback<ChatResponse>() {
            @Override
            public void onResponse(Call<ChatResponse> call, Response<ChatResponse> response) {
                progressBar.setVisibility(View.GONE);
                btnSend.setEnabled(true);

                if (response.isSuccessful() && response.body() != null) {
                    ChatResponse botRes = response.body();
                    String answer = botRes.answer != null ? botRes.answer : "I couldn't find specific notes on that topic.";
                    adapter.addMessage(new ChatMessage(answer, false, botRes.sources));
                    rvChat.smoothScrollToPosition(adapter.getItemCount() - 1);
                } else {
                    adapter.addMessage(new ChatMessage("Unable to query study notes right now. Please verify your backend server is running.", false, null));
                    rvChat.smoothScrollToPosition(adapter.getItemCount() - 1);
                }
            }

            @Override
            public void onFailure(Call<ChatResponse> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                btnSend.setEnabled(true);
                adapter.addMessage(new ChatMessage("Connection failed: " + t.getMessage(), false, null));
                rvChat.smoothScrollToPosition(adapter.getItemCount() - 1);
            }
        });
    }
}
