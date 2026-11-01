package com.college.campusai.adapters;

import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.EmailModels.EmailItem;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class EmailAdapter extends RecyclerView.Adapter<EmailAdapter.EmailViewHolder> {

    public interface OnEmailClickListener {
        void onEmailClick(EmailItem email);
    }

    private final List<EmailItem> emails = new ArrayList<>();
    private final OnEmailClickListener listener;
    private final Set<Integer> starredEmailIds = new HashSet<>();

    public EmailAdapter(OnEmailClickListener listener) {
        this.listener = listener;
    }

    public void setEmails(List<EmailItem> newEmails) {
        emails.clear();
        if (newEmails != null) {
            emails.addAll(newEmails);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public EmailViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_email, parent, false);
        return new EmailViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull EmailViewHolder holder, int position) {
        EmailItem item = emails.get(position);
        holder.bind(item, listener, starredEmailIds.contains(item.id), (emailId, isStarred) -> {
            if (isStarred) {
                starredEmailIds.add(emailId);
            } else {
                starredEmailIds.remove(emailId);
            }
        });
    }

    @Override
    public int getItemCount() {
        return emails.size();
    }

    interface OnStarToggleListener {
        void onStarToggle(int emailId, boolean isStarred);
    }

    static class EmailViewHolder extends RecyclerView.ViewHolder {
        private final TextView tvSubject;
        private final TextView tvSender;
        private final TextView tvDate;
        private final TextView tvCategory;
        private final TextView tvImportance;
        private final View viewUnread;
        private final View viewWarning;
        private final ImageView ivStar;

        public EmailViewHolder(@NonNull View itemView) {
            super(itemView);
            tvSubject = itemView.findViewById(R.id.tv_email_subject);
            tvSender = itemView.findViewById(R.id.tv_email_sender);
            tvDate = itemView.findViewById(R.id.tv_email_date);
            tvCategory = itemView.findViewById(R.id.tv_email_category);
            tvImportance = itemView.findViewById(R.id.tv_email_importance);
            viewUnread = itemView.findViewById(R.id.view_unread_dot);
            viewWarning = itemView.findViewById(R.id.view_uncertain_warning);
            ivStar = itemView.findViewById(R.id.iv_email_star);
        }

        public void bind(final EmailItem item, final OnEmailClickListener listener, boolean isStarred, OnStarToggleListener starListener) {
            tvSubject.setText(item.subject != null ? item.subject : "(No Subject)");
            tvSender.setText(item.sender != null ? item.sender : "College Admin");

            String dateStr = item.receivedAt != null ? item.receivedAt.split("T")[0] : "";
            tvDate.setText(dateStr);

            // Category styling
            String cat = item.category != null ? item.category.toUpperCase() : "GENERAL";
            tvCategory.setText(cat);
            applyCategoryStyle(tvCategory, cat);

            // Importance Badge styling
            String imp = item.importance != null ? item.importance.toUpperCase() : "MEDIUM";
            tvImportance.setText(imp);
            applyImportanceStyle(tvImportance, imp);

            viewUnread.setVisibility(item.isRead ? View.INVISIBLE : View.VISIBLE);
            viewWarning.setVisibility(item.uncertain ? View.VISIBLE : View.GONE);

            // Star bookmark toggle
            updateStarIcon(isStarred);
            ivStar.setOnClickListener(v -> {
                boolean newStarred = !isStarred;
                updateStarIcon(newStarred);
                if (starListener != null) {
                    starListener.onStarToggle(item.id, newStarred);
                }
            });

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onEmailClick(item);
                }
            });
        }

        private void updateStarIcon(boolean isStarred) {
            if (isStarred) {
                ivStar.setImageResource(R.drawable.ic_star_filled);
                ivStar.setColorFilter(Color.parseColor("#F59E0B"));
            } else {
                ivStar.setImageResource(R.drawable.ic_star_outline);
                ivStar.setColorFilter(Color.parseColor("#94A3B8"));
            }
        }

        private void applyCategoryStyle(TextView tv, String cat) {
            int textColor;
            int bgColor;
            if (cat.contains("TIMETABLE") || cat.contains("CLASSROOM")) {
                textColor = Color.parseColor("#2E7D32");
                bgColor = Color.parseColor("#E8F5E9");
            } else if (cat.contains("EXAM")) {
                textColor = Color.parseColor("#7C3AED");
                bgColor = Color.parseColor("#F3E8FF");
            } else if (cat.contains("NOTICE")) {
                textColor = Color.parseColor("#D97706");
                bgColor = Color.parseColor("#FEF3C7");
            } else if (cat.contains("EVENT")) {
                textColor = Color.parseColor("#8B5CF6");
                bgColor = Color.parseColor("#EDE9FE");
            } else if (cat.contains("ASSIGNMENT")) {
                textColor = Color.parseColor("#2563EB");
                bgColor = Color.parseColor("#DBEAFE");
            } else {
                textColor = Color.parseColor("#475569");
                bgColor = Color.parseColor("#F1F5F9");
            }

            tv.setTextColor(textColor);
            GradientDrawable gd = new GradientDrawable();
            gd.setCornerRadius(12f);
            gd.setColor(bgColor);
            tv.setBackground(gd);
        }

        private void applyImportanceStyle(TextView tv, String imp) {
            int textColor;
            int bgColor;
            if ("HIGH".equals(imp)) {
                textColor = Color.parseColor("#DC2626");
                bgColor = Color.parseColor("#FEE2E2");
            } else if ("LOW".equals(imp)) {
                textColor = Color.parseColor("#16A34A");
                bgColor = Color.parseColor("#DCFCE7");
            } else {
                textColor = Color.parseColor("#D97706");
                bgColor = Color.parseColor("#FEF3C7");
            }

            tv.setTextColor(textColor);
            GradientDrawable gd = new GradientDrawable();
            gd.setCornerRadius(10f);
            gd.setColor(bgColor);
            tv.setBackground(gd);
        }
    }
}
