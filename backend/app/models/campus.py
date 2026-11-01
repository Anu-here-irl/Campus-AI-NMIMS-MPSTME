"""Indoor Campus Map and Room models."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class CampusFloor(Base):
    __tablename__ = "campus_floors"

    id = Column(Integer, primary_key=True, index=True)
    floor_name = Column(String(100), nullable=False)  # e.g., "Ground Floor", "Floor 1", "Floor 2"
    floor_order = Column(Integer, nullable=False, unique=True)
    plan_ref = Column(String(500), nullable=True)  # Image file reference or placeholder asset

    rooms = relationship("CampusRoom", back_populates="floor", cascade="all, delete-orphan")
    nodes = relationship("CampusRouteNode", back_populates="floor", cascade="all, delete-orphan")


class CampusRoom(Base):
    __tablename__ = "campus_rooms"

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("campus_floors.id", ondelete="CASCADE"), nullable=False, index=True)
    room_code = Column(String(50), nullable=False, index=True)  # e.g. "204", "Lab 3", "Seminar Hall"
    room_name = Column(String(255), nullable=False)
    room_type = Column(String(50), default="CLASSROOM")  # CLASSROOM, LAB, FACULTY, AUDITORIUM, OFFICE, WASHROOM
    map_x = Column(Float, nullable=True)  # Normalized 0.0 - 1.0 coordinate on floor plan image
    map_y = Column(Float, nullable=True)
    details = Column(Text, nullable=True)
    floor = relationship("CampusFloor", back_populates="rooms")

    @property
    def floor_order(self) -> int:
        return self.floor.floor_order if self.floor else 0


class CampusRouteNode(Base):
    __tablename__ = "campus_route_nodes"

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, ForeignKey("campus_floors.id", ondelete="CASCADE"), nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    node_type = Column(String(50), default="CORRIDOR")  # CORRIDOR, STAIRS, ELEVATOR, ENTRANCE, ROOM_DOOR

    floor = relationship("CampusFloor", back_populates="nodes")


class CampusRouteEdge(Base):
    __tablename__ = "campus_route_edges"

    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(Integer, ForeignKey("campus_route_nodes.id", ondelete="CASCADE"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("campus_route_nodes.id", ondelete="CASCADE"), nullable=False)
    distance = Column(Float, default=1.0)
