package com.college.campusai.adapters;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.CampusMapModels.FloorPlan;
import com.college.campusai.models.CampusMapModels.RoomBlock;

import java.util.ArrayList;
import java.util.List;

public class RoomSearchAdapter extends RecyclerView.Adapter<RoomSearchAdapter.SearchViewHolder> {

    public static class SearchResultEntry {
        public final FloorPlan floor;
        public final RoomBlock room;

        public SearchResultEntry(FloorPlan floor, RoomBlock room) {
            this.floor = floor;
            this.room = room;
        }
    }

    public interface OnSearchResultClickListener {
        void onResultClick(FloorPlan floor, RoomBlock room);
    }

    private final List<SearchResultEntry> results = new ArrayList<>();
    private final OnSearchResultClickListener listener;

    public RoomSearchAdapter(OnSearchResultClickListener listener) {
        this.listener = listener;
    }

    public void setResults(List<SearchResultEntry> newResults) {
        results.clear();
        if (newResults != null) {
            results.addAll(newResults);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public SearchViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_room_search_result, parent, false);
        return new SearchViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull SearchViewHolder holder, int position) {
        SearchResultEntry entry = results.get(position);
        holder.bind(entry, listener);
    }

    @Override
    public int getItemCount() {
        return results.size();
    }

    static class SearchViewHolder extends RecyclerView.ViewHolder {
        TextView tvCode, tvName, tvSubtitle, tvVerified;

        public SearchViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCode = itemView.findViewById(R.id.tv_search_code);
            tvName = itemView.findViewById(R.id.tv_search_name);
            tvSubtitle = itemView.findViewById(R.id.tv_search_subtitle);
            tvVerified = itemView.findViewById(R.id.tv_search_verified_badge);
        }

        public void bind(final SearchResultEntry entry, final OnSearchResultClickListener listener) {
            RoomBlock r = entry.room;
            FloorPlan f = entry.floor;

            tvCode.setText(r.code);
            tvCode.setTextColor(r.getBorderColor());

            tvName.setText(r.name);
            String subtitle = (f != null ? f.floorName : "Campus") + " • " + r.getCategoryDisplayName();
            tvSubtitle.setText(subtitle);

            if (r.verified) {
                tvVerified.setText("✓ Verified");
                tvVerified.setTextColor(Color.parseColor("#059669"));
            } else {
                tvVerified.setText("⚠️ Unverified");
                tvVerified.setTextColor(Color.parseColor("#D97706"));
            }

            itemView.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onResultClick(f, r);
                }
            });
        }
    }
}
