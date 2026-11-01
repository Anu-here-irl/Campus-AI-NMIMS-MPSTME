package com.college.campusai.models;

import android.graphics.Color;
import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class CampusMapModels {

    public static class CampusManifest implements Serializable {
        @SerializedName("campus_name")
        public String campusName;
        public String location;
        public List<FloorPlan> floors = new ArrayList<>();
    }

    public static class FloorPlan implements Serializable {
        @SerializedName("floor_id")
        public String floorId;
        @SerializedName("floor_order")
        public int floorOrder;
        @SerializedName("floor_name")
        public String floorName;
        @SerializedName("plan_image")
        public String planImage;
        public float width = 1000f;
        public float height = 1350f;
        public List<RoomBlock> rooms = new ArrayList<>();

        @Override
        public String toString() {
            return floorName != null ? floorName : floorId;
        }
    }

    public static class RoomBlock implements Serializable {
        public String code;
        public String name;
        public String category; // CLASSROOM, EXAM, LAB, OFFICE, LIFT, LOBBY, COMMON_AREA, RESTROOM, STAIRCASE, UTILITY
        public float x;
        public float y;
        public float width;
        public float height;
        public boolean verified = true;
        public String notes;

        public boolean matchesQuery(String query) {
            if (query == null || query.trim().isEmpty()) {
                return true;
            }
            String q = query.trim().toLowerCase();
            return (code != null && code.toLowerCase().contains(q))
                    || (name != null && name.toLowerCase().contains(q))
                    || (category != null && category.toLowerCase().contains(q))
                    || (notes != null && notes.toLowerCase().contains(q));
        }

        public boolean containsPoint(float px, float py) {
            return px >= x && px <= (x + width) && py >= y && py <= (y + height);
        }

        public int getBorderColor() {
            if (category == null) return Color.parseColor("#475569");
            switch (category.toUpperCase()) {
                case "CLASSROOM":
                    return Color.parseColor("#2563EB"); // Blue 600
                case "EXAM":
                    return Color.parseColor("#7C3AED"); // Purple 600
                case "LAB":
                    return Color.parseColor("#059669"); // Emerald 600
                case "OFFICE":
                    return Color.parseColor("#D97706"); // Amber 600
                case "LIFT":
                    return Color.parseColor("#0891B2"); // Cyan 600
                case "LOBBY":
                    return Color.parseColor("#475569"); // Slate 600
                case "COMMON_AREA":
                    return Color.parseColor("#4F46E5"); // Indigo 600
                case "RESTROOM":
                    return Color.parseColor("#E11D48"); // Rose 600
                case "STAIRCASE":
                    return Color.parseColor("#EA580C"); // Orange 600
                case "UTILITY":
                default:
                    return Color.parseColor("#64748B"); // Gray 500
            }
        }

        public int getFillColor() {
            if (category == null) return Color.parseColor("#F1F5F9");
            switch (category.toUpperCase()) {
                case "CLASSROOM":
                    return Color.parseColor("#EFF6FF"); // Blue 50
                case "EXAM":
                    return Color.parseColor("#F5F3FF"); // Purple 50
                case "LAB":
                    return Color.parseColor("#ECFDF5"); // Emerald 50
                case "OFFICE":
                    return Color.parseColor("#FFFBEB"); // Amber 50
                case "LIFT":
                    return Color.parseColor("#ECFEFF"); // Cyan 50
                case "LOBBY":
                    return Color.parseColor("#F8FAFC"); // Slate 50
                case "COMMON_AREA":
                    return Color.parseColor("#EEF2FF"); // Indigo 50
                case "RESTROOM":
                    return Color.parseColor("#FFF1F2"); // Rose 50
                case "STAIRCASE":
                    return Color.parseColor("#FFF7ED"); // Orange 50
                case "UTILITY":
                default:
                    return Color.parseColor("#F1F5F9"); // Gray 100
            }
        }

        public String getCategoryDisplayName() {
            if (category == null) return "Facility";
            switch (category.toUpperCase()) {
                case "CLASSROOM": return "Classroom";
                case "EXAM": return "Examination Hall";
                case "LAB": return "Laboratory";
                case "OFFICE": return "Office / Admin";
                case "LIFT": return "Elevator / Lift";
                case "LOBBY": return "Lobby / Corridor";
                case "COMMON_AREA": return "Common / Atrium";
                case "RESTROOM": return "Washroom";
                case "STAIRCASE": return "Emergency Staircase";
                case "UTILITY": return "Utility / Systems";
                default: return category;
            }
        }
    }
}
