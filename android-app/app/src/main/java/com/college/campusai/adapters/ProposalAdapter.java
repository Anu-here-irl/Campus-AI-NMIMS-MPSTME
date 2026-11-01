package com.college.campusai.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.EventModels.EventItem;

import java.util.ArrayList;
import java.util.List;

public class ProposalAdapter extends RecyclerView.Adapter<ProposalAdapter.ProposalViewHolder> {

    public interface OnProposalActionListener {
        void onConfirm(EventItem event);
        void onReject(EventItem event);
    }

    private final List<EventItem> proposals = new ArrayList<>();
    private final OnProposalActionListener listener;

    public ProposalAdapter(OnProposalActionListener listener) {
        this.listener = listener;
    }

    public void setProposals(List<EventItem> newProposals) {
        proposals.clear();
        if (newProposals != null) {
            proposals.addAll(newProposals);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ProposalViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_proposal, parent, false);
        return new ProposalViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ProposalViewHolder holder, int position) {
        EventItem item = proposals.get(position);
        holder.bind(item, listener);
    }

    @Override
    public int getItemCount() {
        return proposals.size();
    }

    static class ProposalViewHolder extends RecyclerView.ViewHolder {
        private final TextView tvTitle;
        private final TextView tvSubject;
        private final TextView tvSummary;
        private final TextView tvLocation;
        private final Button btnConfirm;
        private final Button btnReject;

        public ProposalViewHolder(@NonNull View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tv_proposal_title);
            tvSubject = itemView.findViewById(R.id.tv_proposal_subject);
            tvSummary = itemView.findViewById(R.id.tv_proposal_summary);
            tvLocation = itemView.findViewById(R.id.tv_proposal_location);
            btnConfirm = itemView.findViewById(R.id.btn_confirm_proposal);
            btnReject = itemView.findViewById(R.id.btn_reject_proposal);
        }

        public void bind(final EventItem item, final OnProposalActionListener listener) {
            tvTitle.setText(item.title);
            tvSubject.setText(item.subject != null ? item.subject : item.eventType);
            tvSummary.setText(item.summary != null ? item.summary : "Schedule change detected from email.");
            tvLocation.setText(item.location != null ? ("New Location: " + item.location) : "");

            btnConfirm.setOnClickListener(v -> {
                if (listener != null) listener.onConfirm(item);
            });

            btnReject.setOnClickListener(v -> {
                if (listener != null) listener.onReject(item);
            });
        }
    }
}
