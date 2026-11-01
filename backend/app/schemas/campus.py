"""Campus Map and Navigation Pydantic schemas."""

from pydantic import BaseModel


class CampusRoomResponse(BaseModel):
    id: int
    floor_id: int
    room_code: str
    room_name: str
    room_type: str
    map_x: float | None = None
    map_y: float | None = None
    floor_order: int | None = None
    details: str | None = None

    class Config:
        from_attributes = True


class CampusFloorResponse(BaseModel):
    id: int
    floor_name: str
    floor_order: int
    plan_ref: str | None = None
    rooms: list[CampusRoomResponse] = []

    class Config:
        from_attributes = True


class RouteStep(BaseModel):
    instruction: str
    distance: float


class RouteResponse(BaseModel):
    from_room: str
    to_room: str
    total_distance: float
    steps: list[RouteStep]
    nodes: list[dict]
