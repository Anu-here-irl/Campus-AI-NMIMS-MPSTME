package com.college.campusai.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;

public class CampusModels {

    public static class CampusFloor implements Serializable {
        public int id;
        @SerializedName("floor_name")
        public String floorName;
        @SerializedName("floor_order")
        public int floorOrder;
        @SerializedName("plan_ref")
        public String planRef;
        public List<CampusRoom> rooms;
    }

    public static class CampusRoom implements Serializable {
        public int id;
        @SerializedName("floor_id")
        public int floorId;
        @SerializedName("room_code")
        public String roomCode;
        @SerializedName("room_name")
        public String roomName;
        @SerializedName("room_type")
        public String roomType;
        @SerializedName("map_x")
        public Double mapX;
        @SerializedName("map_y")
        public Double mapY;
        public String details;
    }

    public static class RouteResponse implements Serializable {
        @SerializedName("from_room")
        public String fromRoom;
        @SerializedName("to_room")
        public String toRoom;
        @SerializedName("total_distance")
        public double totalDistance;
        public List<RouteStep> steps;
    }

    public static class RouteStep implements Serializable {
        public String instruction;
        public double distance;
    }
}
