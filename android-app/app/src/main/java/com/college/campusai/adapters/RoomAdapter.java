package com.college.campusai.adapters;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.college.campusai.R;
import com.college.campusai.models.CampusModels.CampusRoom;

import java.util.ArrayList;
import java.util.List;

public class RoomAdapter extends RecyclerView.Adapter<RoomAdapter.RoomViewHolder> {

    public interface OnRoomClickListener {
        void onRoomClick(CampusRoom room);
    }

    private final List<CampusRoom> rooms = new ArrayList<>();
    private final OnRoomClickListener listener;

    public RoomAdapter(OnRoomClickListener listener) {
        this.listener = listener;
    }

    public void setRooms(List<CampusRoom> newRooms) {
        rooms.clear();
        if (newRooms != null) {
            rooms.addAll(newRooms);
        }
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public RoomViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_room, parent, false);
        return new RoomViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull RoomViewHolder holder, int position) {
        CampusRoom r = rooms.get(position);
        holder.bind(r, listener);
    }

    @Override
    public int getItemCount() {
        return rooms.size();
    }

    static class RoomViewHolder extends RecyclerView.ViewHolder {
        TextView tvCode, tvName, tvType, tvDetails;

        public RoomViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCode = itemView.findViewById(R.id.tv_room_code);
            tvName = itemView.findViewById(R.id.tv_room_name);
            tvType = itemView.findViewById(R.id.tv_room_type);
            tvDetails = itemView.findViewById(R.id.tv_room_details);
        }

        public void bind(final CampusRoom r, final OnRoomClickListener listener) {
            tvCode.setText(r.roomCode);
            tvName.setText(r.roomName);
            tvType.setText(r.roomType);
            tvDetails.setText(r.details != null ? r.details : "");

            itemView.setOnClickListener(v -> {
                if (listener != null) listener.onRoomClick(r);
            });
        }
    }
}
